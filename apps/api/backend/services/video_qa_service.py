import json
import os
import re
import subprocess
from typing import Any, Dict, List, Optional

import cv2
import numpy as np

from backend.config import logger


def audit_rendered_video(
    video_path: str,
    expect_audio: bool = True,
    target_lufs: float = -14.0,
) -> Dict[str, Any]:
    """
    Lightweight automated post-render Video & Audio QA gate inspired by showtime qa & motionmaxxing look.py.
    Verifies stream integrity, Frame 0 (anti-black opening), Integrated LUFS & True Peak,
    opening leading silence (< 0.5s), and frozen frame stretches (>= 2.5s).
    """
    issues: List[Dict[str, str]] = []
    report: Dict[str, Any] = {
        "status": "PASS",
        "duration_sec": 0.0,
        "resolution": "unknown",
        "audio_sample_rate": None,
        "lufs": None,
        "true_peak_db": None,
        "first_frame_ok": True,
        "first_frame_luma": None,
        "leading_silence_sec": 0.0,
        "frozen_count": 0,
        "issues": issues,
        "summary": "",
    }

    if not video_path or not os.path.exists(video_path):
        issues.append({"rule": "unreadable", "severity": "FAIL", "message": "Output MP4 tidak ditemukan."})
        report["status"] = "FAIL"
        report["summary"] = "FAIL | File tidak ditemukan"
        return report

    # 1. Stream Integrity via ffprobe
    has_audio = False
    v_dur = 0.0
    a_dur = 0.0
    try:
        probe_cmd = [
            "ffprobe", "-v", "error",
            "-show_streams", "-show_format",
            "-of", "json", str(video_path),
        ]
        probe_res = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=10)
        if probe_res.returncode != 0 or not probe_res.stdout:
            issues.append({"rule": "unreadable", "severity": "FAIL", "message": "FFprobe gagal membaca metadata MP4."})
            report["status"] = "FAIL"
            report["summary"] = "FAIL | Metadata korup"
            return report

        pdata = json.loads(probe_res.stdout)
        streams = pdata.get("streams", [])
        v_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
        a_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)
        fmt_dur = float(pdata.get("format", {}).get("duration") or 0.0)
        report["duration_sec"] = round(fmt_dur, 2)

        if not v_stream:
            issues.append({"rule": "no_video", "severity": "FAIL", "message": "Stream video tidak ditemukan."})
        else:
            w = int(v_stream.get("width") or 0)
            h = int(v_stream.get("height") or 0)
            report["resolution"] = f"{w}x{h}"
            if (w % 2 != 0) or (h % 2 != 0):
                issues.append({"rule": "odd_dimensions", "severity": "FAIL", "message": f"Dimensi ganjil ({w}x{h})."})
            pix_fmt = str(v_stream.get("pix_fmt") or "")
            if pix_fmt and pix_fmt != "yuv420p":
                issues.append({"rule": "pix_fmt", "severity": "WARN", "message": f"Pixel format {pix_fmt} (ideal yuv420p)."})
            v_dur = float(v_stream.get("duration") or fmt_dur or 0.0)

        if a_stream:
            has_audio = True
            sr = int(a_stream.get("sample_rate") or 0)
            report["audio_sample_rate"] = sr
            a_dur = float(a_stream.get("duration") or fmt_dur or 0.0)
            if sr and sr != 48000:
                issues.append({"rule": "audio_sample_rate", "severity": "WARN", "message": f"Audio {sr} Hz (standar platform 48000 Hz)."})
            if v_dur > 0 and a_dur > 0 and abs(v_dur - a_dur) > 0.25:
                issues.append({"rule": "av_length", "severity": "WARN", "message": f"Selisih durasi A/V {abs(v_dur - a_dur):.2f}s."})
        elif expect_audio:
            issues.append({"rule": "no_audio", "severity": "WARN", "message": "Tidak ada stream audio."})
    except Exception as e:
        logger.debug(f"QA ffprobe error: {e}")

    # 2. Frame-0 Opening Check (Anti-Black / Anti-Flat First Frame)
    try:
        cap = cv2.VideoCapture(str(video_path))
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_POS_MSEC, 50.0)
            ok, frame = cap.read()
            cap.release()
            if ok and frame is not None:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                luma_mean = float(np.mean(gray))
                luma_std = float(np.std(gray))
                report["first_frame_luma"] = round(luma_mean, 1)
                if luma_mean < 10.0:
                    report["first_frame_ok"] = False
                    issues.append({
                        "rule": "first_frame_black",
                        "severity": "WARN",
                        "message": f"Frame 0 terlalu gelap/hitam (luma {luma_mean:.1f}).",
                    })
                elif luma_std < 2.0:
                    report["first_frame_ok"] = False
                    issues.append({
                        "rule": "first_frame_flat",
                        "severity": "WARN",
                        "message": "Frame 0 berupa warna datar polos tanpa objek.",
                    })
    except Exception as e:
        logger.debug(f"QA frame-0 check error: {e}")

    # 3. Audio Loudness (LUFS), True Peak, and Opening Leading Silence
    if has_audio:
        try:
            ebur_cmd = [
                "ffmpeg", "-hide_banner", "-nostats", "-i", str(video_path),
                "-map", "0:a:0",
                "-af", "ebur128=peak=true",
                "-f", "null", "-",
            ]
            ebur_res = subprocess.run(ebur_cmd, capture_output=True, text=True, timeout=20)
            err = ebur_res.stderr or ""
            # Grab final Summary block values
            i_matches = re.findall(r"I:\s*(-?[\d\.]+)\s*LUFS", err)
            tp_matches = re.findall(r"Peak:\s*(-?[\d\.]+)\s*dBFS", err)
            if i_matches:
                lufs = float(i_matches[-1])
                report["lufs"] = round(lufs, 1)
                if lufs < -55.0:
                    issues.append({"rule": "silent_audio", "severity": "FAIL", "message": f"Audio sangat senyap ({lufs:.1f} LUFS)."})
                elif abs(lufs - target_lufs) > 3.0:
                    issues.append({"rule": "loudness", "severity": "WARN", "message": f"Loudness {lufs:.1f} LUFS (target {target_lufs:.0f} LUFS)."})
            if tp_matches:
                tp = float(tp_matches[-1])
                report["true_peak_db"] = round(tp, 1)
                if tp > -0.3:
                    issues.append({"rule": "true_peak", "severity": "WARN", "message": f"True peak tinggi ({tp:.1f} dBTP, rawan clipping)."})
        except Exception as e:
            logger.debug(f"QA loudness error: {e}")

        # Leading silence check (first 3 seconds only -> super fast)
        try:
            sil_cmd = [
                "ffmpeg", "-hide_banner", "-nostats", "-t", "3.0", "-i", str(video_path),
                "-map", "0:a:0",
                "-af", "silencedetect=noise=-42dB:d=0.35",
                "-f", "null", "-",
            ]
            sil_res = subprocess.run(sil_cmd, capture_output=True, text=True, timeout=8)
            serr = sil_res.stderr or ""
            s_starts = [float(x) for x in re.findall(r"silence_start:\s*(-?[\d\.]+)", serr)]
            s_ends = [float(x) for x in re.findall(r"silence_end:\s*([\d\.]+)", serr)]
            if s_starts and s_starts[0] <= 0.08:
                lead_end = s_ends[0] if s_ends else 3.0
                report["leading_silence_sec"] = round(lead_end, 2)
                if lead_end >= 0.50:
                    issues.append({
                        "rule": "leading_silence",
                        "severity": "WARN",
                        "message": f"Ada jeda hening {lead_end:.2f}s di awal klip (aktifkan Auto-Trim Dead Air).",
                    })
        except Exception as e:
            logger.debug(f"QA leading silence error: {e}")

    # 4. Frozen Segment Detection (>= 2.5s freeze)
    try:
        frz_cmd = [
            "ffmpeg", "-hide_banner", "-nostats", "-i", str(video_path),
            "-an", "-vf", "scale=160:-2,freezedetect=n=-50dB:d=2.5",
            "-f", "null", "-",
        ]
        frz_res = subprocess.run(frz_cmd, capture_output=True, text=True, timeout=20)
        frz_hits = re.findall(r"freeze_duration:\s*([\d\.]+)", frz_res.stderr or "")
        report["frozen_count"] = len(frz_hits)
        if frz_hits:
            max_frz = max(float(x) for x in frz_hits)
            issues.append({
                "rule": "frozen",
                "severity": "WARN",
                "message": f"Terdeteksi {len(frz_hits)} segmen statis/freeze (maks {max_frz:.1f}s).",
            })
    except Exception as e:
        logger.debug(f"QA freeze detect error: {e}")

    # Final Verdict Aggregation
    if any(i["severity"] == "FAIL" for i in issues):
        report["status"] = "FAIL"
    elif any(i["severity"] == "WARN" for i in issues):
        report["status"] = "WARN"
    else:
        report["status"] = "PASS"

    parts = [report["status"]]
    if report["lufs"] is not None:
        parts.append(f"{report['lufs']} LUFS")
    if report["true_peak_db"] is not None:
        parts.append(f"TP {report['true_peak_db']} dB")
    if report["audio_sample_rate"]:
        parts.append(f"{int(report['audio_sample_rate'] / 1000)}kHz")
    parts.append("Frame 0 OK" if report["first_frame_ok"] else "Frame 0 Check")
    report["summary"] = " | ".join(parts)
    return report
