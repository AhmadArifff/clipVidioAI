#!/usr/bin/env python3
"""
ClipVidio AI - Tier-1 Automated Verification Kernel (.agents/scripts/qa-kernel.py)
Verifies Python syntax, Pydantic contracts, phase-safe mono guard, Smart Silence Jumpcut
with word re-timing, end-to-end FFmpeg compositing (High-Contrast Box + Reaction Cam +
BGM Highpass/Ducking + 48kHz AAC), Sidecar SRT, Sharpest Cover JPG, Post-Render QA Gate,
and Anti-Slop Rule R-02 (zero em-dash) compliance.
"""

import compileall
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
API_DIR = ROOT_DIR / "apps" / "api"
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))


def _run(cmd, timeout=30):
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if res.returncode != 0:
        raise RuntimeError(f"Command failed ({res.returncode}): {' '.join(cmd)}\nSTDERR: {(res.stderr or '')[:500]}")
    return res


def check_1_compile_backend():
    ok = compileall.compile_dir(str(API_DIR / "backend"), quiet=1)
    assert ok, "compileall found Python syntax errors under apps/api/backend"
    return "All backend Python modules compiled cleanly"


def check_2_schemas_and_parser():
    from backend.schemas.render import RenderSettingsModel
    from backend.schemas.analyze import ViralClip
    from backend.routers.analyze import parse_lenient_json_analysis

    rs = RenderSettingsModel(
        caption_style="high_contrast_box",
        silence_cut_mode="natural",
        reaction_cam_border_color="neon_purple",
    )
    assert rs.silence_cut_mode == "natural"
    assert rs.caption_style == "high_contrast_box"

    sample_json = json.dumps({
        "summary": "Ringkasan diskusi strategi bisnis. #bisnis #viral",
        "clips": [
            {
                "title": "Strategi Konten Founder Tanpa Modal Besar",
                "start_time": 12.0,
                "end_time": 42.0,
                "hook_time": 12.5,
                "virality_score": 91,
                "key_quotes": ["Kebanyakan kreator salah di tiga detik pertama"],
                "title_suggestion": "Kesalahan Fatal Tiga Detik Pertama",
                "caption_suggestion": "Pembicara membedah pola hook tiga detik.",
                "hashtag_suggestion": "#konten #shorts",
                "framing_type": "controversial",
                "open_loop_question": "Kenapa 90% video langsung di-skip di detik kedua?",
                "payoff_time": 37.5,
                "muted_hook_overlay": "Saya Bongkar Kesalahan Detik Pertama",
            }
        ],
    })
    parsed = parse_lenient_json_analysis(sample_json, channel="Budi", lang_code="id")
    assert parsed and len(parsed["clips"]) == 1
    c = parsed["clips"][0]
    assert c["framing_type"] == "controversial"
    assert "skip" in c["open_loop_question"].lower()
    assert c["payoff_time"] == 37.5
    assert c["muted_hook_overlay"], "muted_hook_overlay missing"
    assert not c["muted_hook_overlay"].lower().startswith("saya "), (
        f"First-person pronoun leaked in muted_hook_overlay: {c['muted_hook_overlay']}"
    )

    vc = ViralClip(
        title=c["title"],
        start_time=c["start_time"],
        end_time=c["end_time"],
        hook_time=c["hook_time"],
        virality_score=c["virality_score"],
        key_quotes=c["key_quotes"],
        transcript="Kebanyakan kreator salah di tiga detik pertama.",
        framing_type=c["framing_type"],
        open_loop_question=c["open_loop_question"],
        payoff_time=c["payoff_time"],
        muted_hook_overlay=c["muted_hook_overlay"],
    )
    assert vc.framing_type == "controversial"
    return "RenderSettingsModel, ViralClip, and lenient AI parser passed contract checks"


def check_3_phase_safe_mono(tmp: Path):
    from backend.video_engine import detect_safe_mono_pan

    in_phase = tmp / "in_phase.wav"
    inv_phase = tmp / "inverted_phase.wav"

    _run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "lavfi", "-i", "aevalsrc=0.45*sin(2*PI*440*t)|0.45*sin(2*PI*440*t):s=48000:d=2.0",
        str(in_phase),
    ])
    _run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "lavfi", "-i", "aevalsrc=0.45*sin(2*PI*440*t)|-0.45*sin(2*PI*440*t):s=48000:d=2.0",
        str(inv_phase),
    ])

    pan_normal = detect_safe_mono_pan(str(in_phase))
    pan_inverted = detect_safe_mono_pan(str(inv_phase))

    assert "0.5*c0+0.5*c1" in pan_normal, f"Expected stereo sum for in-phase audio, got: {pan_normal}"
    assert "0.5*c0+0.5*c1" not in pan_inverted, f"Phase inversion was NOT guarded: {pan_inverted}"
    assert pan_inverted in ("pan=stereo|c0=c0|c1=c0", "pan=stereo|c0=c1|c1=c1"), f"Unexpected safe pan: {pan_inverted}"
    return f"In-phase -> sum, Inverted-phase -> {pan_inverted}"


def check_4_silence_jumpcut(tmp: Path):
    from backend.services.silence_cutter_service import apply_silence_cut
    from backend.video_engine import is_valid_mp4

    src = tmp / "silence_src.mp4"
    out = tmp / "silence_cut.mp4"
    # 6.0s video with audio active at 1.5-2.5s and 4.2-5.2s, silent elsewhere
    _run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "lavfi", "-i", "testsrc2=size=640x360:rate=30:duration=6.0",
        "-f", "lavfi", "-i",
        "aevalsrc='if(between(t,1.5,2.5)+between(t,4.2,5.2),0.4*sin(2*PI*330*t),0)':s=48000:d=6.0",
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", "48000", "-ac", "2",
        str(src),
    ])

    words = [
        {"word": "Halo", "start": 1.50, "end": 2.00},
        {"word": "semua.", "start": 2.00, "end": 2.50},
        {"word": "Ini", "start": 4.20, "end": 4.70},
        {"word": "tes", "start": 4.70, "end": 5.20},
    ]
    res = apply_silence_cut(str(src), str(out), words=words, duration=6.0, mode="natural")
    assert res["applied"] is True, f"Silence cut did not apply: {res}"
    assert res["removed_sec"] >= 1.8, f"Expected >= 1.8s removed, got {res['removed_sec']}"
    assert is_valid_mp4(str(out)), "Silence-cut MP4 is invalid"
    assert res["duration"] < 4.5, f"Cut duration not shortened: {res['duration']}"

    rw = res["words"]
    assert len(rw) == len(words), "Word count changed after re-timing"
    assert rw[0]["start"] <= 0.20, f"Head dead-air not trimmed properly, first word starts at {rw[0]['start']}s"
    for i in range(len(rw)):
        assert rw[i]["end"] > rw[i]["start"], f"Invalid word range: {rw[i]}"
        if i > 0:
            assert rw[i]["start"] >= rw[i - 1]["start"], f"Non-monotonic word timing: {rw}"
    return f"Trimmed {res['removed_sec']:.2f}s (6.00s -> {res['duration']:.2f}s), first word at {rw[0]['start']:.2f}s"


def check_5_e2e_render_srt_cover_qa(tmp: Path):
    from backend.video_engine import (
        generate_ass_file,
        generate_srt_file,
        extract_cover_thumbnail,
        render_clip_to_mp4,
        is_valid_mp4,
    )
    from backend.services.video_qa_service import audit_rendered_video

    main_src = tmp / "main_clip.mp4"
    rc_src = tmp / "reaction_cam.mp4"
    bgm_src = tmp / "bgm.wav"
    ass_path = tmp / "subs.ass"
    srt_path = tmp / "subs.srt"
    out_mp4 = tmp / "rendered_final.mp4"
    cover_jpg = tmp / "cover_final.jpg"

    _run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "lavfi", "-i", "testsrc2=size=1280x720:rate=30:duration=4.0",
        "-f", "lavfi", "-i", "aevalsrc=0.35*sin(2*PI*300*t)+0.15*sin(2*PI*620*t)|0.35*sin(2*PI*300*t)+0.15*sin(2*PI*620*t):s=48000:d=4.0",
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", "48000", "-ac", "2",
        str(main_src),
    ])
    _run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "lavfi", "-i", "smptebars=size=320x320:rate=30:duration=4.0",
        "-f", "lavfi", "-i", "aevalsrc=0.1*sin(2*PI*220*t)|0.1*sin(2*PI*220*t):s=48000:d=4.0",
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", "48000", "-ac", "2",
        str(rc_src),
    ])
    _run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "lavfi", "-i", "aevalsrc=0.25*sin(2*PI*90*t)+0.2*sin(2*PI*180*t)|0.25*sin(2*PI*90*t)+0.2*sin(2*PI*180*t):s=48000:d=4.0",
        str(bgm_src),
    ])

    words = [
        {"word": "Ini", "start": 0.10, "end": 0.30},
        {"word": "hook", "start": 0.30, "end": 0.70},
        {"word": "viral", "start": 0.75, "end": 1.30},
        {"word": "untuk", "start": 1.40, "end": 1.90},
        {"word": "audiens", "start": 1.95, "end": 2.60},
        {"word": "Shorts.", "start": 2.65, "end": 3.40},
    ]

    generate_ass_file(
        words=words,
        style_preset="high_contrast_box",
        font_name="Outfit",
        output_ass_path=str(ass_path),
        target_aspect_ratio="9:16",
    )
    ass_txt = ass_path.read_text(encoding="utf-8")
    assert "BorderStyle" in ass_txt and ",3," in ass_txt, "high_contrast_box ASS missing BorderStyle=3"

    srt_res = generate_srt_file(
        words=words,
        output_srt_path=str(srt_path),
        text_case="uppercase",
        speed_ratio=1.03,
    )
    assert srt_res and srt_path.exists()
    srt_txt = srt_path.read_text(encoding="utf-8")
    assert "-->" in srt_txt and "SHORTS." in srt_txt, "Sidecar SRT invalid"

    render_clip_to_mp4(
        video_path=str(main_src),
        output_mp4_path=str(out_mp4),
        aspect_ratio="9:16",
        enable_face_tracking=False,
        ass_subtitles_path=str(ass_path),
        clip_duration=4.0,
        bgm_enabled=True,
        bgm_path=str(bgm_src),
        bgm_volume=0.25,
        hardware_accel="cpu",
        video_polish_enabled=True,
        audio_mastering_enabled=True,
        smart_ducking_enabled=True,
        hook_zoom_enabled=True,
        speed_ramp_ratio=1.03,
        vocal_isolation_mode="center_vocal_extract",
        reaction_cam_enabled=True,
        reaction_cam_file_path=str(rc_src),
        reaction_cam_position="bottom_right",
        reaction_cam_size=24.0,
        reaction_cam_shape="circle",
        reaction_cam_border_color="neon_purple",
        reaction_cam_mute_audio=False,
    )
    assert is_valid_mp4(str(out_mp4)), "E2E rendered MP4 invalid"

    cover_res = extract_cover_thumbnail(str(out_mp4), str(cover_jpg))
    assert cover_res and cover_jpg.exists() and cover_jpg.stat().st_size > 5000, "Cover JPG invalid or too small"

    qa = audit_rendered_video(str(out_mp4), expect_audio=True)
    assert qa["status"] in ("PASS", "WARN"), f"Post-render QA FAIL: {qa}"
    assert qa["resolution"] == "1080x1920", f"Unexpected resolution: {qa['resolution']}"
    assert qa["audio_sample_rate"] == 48000, f"Audio sample rate not 48000 Hz: {qa['audio_sample_rate']}"
    assert qa["first_frame_ok"] is True, f"Frame 0 check failed: {qa}"
    assert qa["lufs"] is not None, f"LUFS not measured: {qa}"

    return f"Render+RC(unmuted)+HighContrastBox+Ducking+SRT+Cover OK | QA: {qa['summary']}"


def check_6_zero_em_dash():
    res = subprocess.run(
        ["git", "status", "--porcelain", "-uall"],
        cwd=str(ROOT_DIR),
        capture_output=True,
        text=True,
        timeout=15,
    )
    offenders = []
    if res.returncode == 0:
        for line in res.stdout.splitlines():
            if len(line) < 4:
                continue
            status = line[:2]
            if "D" in status:
                continue
            rel = line[3:].strip().strip('"')
            if " -> " in rel:
                rel = rel.split(" -> ")[-1].strip('"')
            if rel.startswith(".agents/skills/") or rel.startswith("node_modules/"):
                continue
            p = ROOT_DIR / rel
            if not p.is_file():
                continue
            if p.suffix.lower() not in (".md", ".py", ".ts", ".tsx", ".js", ".json", ".css", ".html"):
                continue
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
                if "\u2014" in content:
                    count = content.count("\u2014")
                    offenders.append(f"{rel} ({count})")
            except Exception:
                pass
    assert not offenders, f"Rule R-02 violation: em dash found in {', '.join(offenders)}"
    return "Zero em dashes across all modified/created workspace files"


def main():
    checks = [
        ("1. Backend Python Compile", lambda _tmp: check_1_compile_backend()),
        ("2. Schemas & AI Open-Loop Parser", lambda _tmp: check_2_schemas_and_parser()),
        ("3. Phase-Safe Stereo-to-Mono Guard", check_3_phase_safe_mono),
        ("4. Smart Silence Jumpcut & Word Re-Timing", check_4_silence_jumpcut),
        ("5. E2E Render + RC(Unmuted) + SRT + Cover + QA Gate", check_5_e2e_render_srt_cover_qa),
        ("6. Anti-Slop Rule R-02 (Zero Em-Dash)", lambda _tmp: check_6_zero_em_dash()),
    ]

    tmp_dir = Path(tempfile.mkdtemp(prefix="clipvidio_qa_"))
    passed = 0
    failed = 0
    print("=" * 72)
    print("ClipVidio AI - Tier-1 QA Kernel")
    print("=" * 72)
    try:
        for label, fn in checks:
            try:
                detail = fn(tmp_dir)
                passed += 1
                print(f"[PASS] {label}\n       {detail}")
            except Exception as exc:
                failed += 1
                print(f"[FAIL] {label}\n       {exc}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print("=" * 72)
    print(f"RESULT: {passed} PASSED, {failed} FAILED")
    print("=" * 72)
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
