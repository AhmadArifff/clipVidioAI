import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from backend.config import is_valid_mp4, logger


SILENCE_CUT_PRESETS: Dict[str, Dict[str, float]] = {
    "natural": {"gap": 0.55, "head_pad": 0.12, "tail_pad": 0.28, "noise_db": -38.0},
    "snappy": {"gap": 0.35, "head_pad": 0.08, "tail_pad": 0.22, "noise_db": -36.0},
}


def _probe_media_duration(video_path: str, fallback: float = 30.0) -> float:
    """Returns shortest valid stream duration (video/audio) so cuts never overrun EOF."""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "stream=codec_type,duration:format=duration",
            "-of", "json",
            str(video_path),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if res.returncode != 0 or not res.stdout:
            return fallback
        import json
        data = json.loads(res.stdout)
        lengths = [
            float(s["duration"])
            for s in data.get("streams", [])
            if s.get("codec_type") in ("audio", "video")
            and s.get("duration") not in (None, "N/A")
        ]
        if lengths:
            return max(0.5, min(lengths))
        fmt_dur = data.get("format", {}).get("duration")
        if fmt_dur not in (None, "N/A"):
            return max(0.5, float(fmt_dur))
    except Exception:
        pass
    return max(0.5, float(fallback))


def _merge_ranges(ranges: List[Tuple[float, float, str]]) -> List[Dict[str, Any]]:
    valid = [(s, e, r) for s, e, r in ranges if e > s + 0.02]
    valid.sort(key=lambda x: x[0])
    merged: List[Dict[str, Any]] = []
    for s, e, reason in valid:
        if not merged or s > merged[-1]["end"]:
            merged.append({"start": s, "end": e, "reasons": [reason]})
        else:
            merged[-1]["end"] = max(merged[-1]["end"], e)
            merged[-1]["reasons"].append(reason)
    return merged


def _detect_audio_silences(video_path: str, noise_db: float, min_gap: float) -> List[Tuple[float, float]]:
    """Fallback FFmpeg silencedetect when word-level transcript timestamps are absent."""
    try:
        cmd = [
            "ffmpeg", "-hide_banner", "-i", str(video_path),
            "-map", "0:a:0",
            "-af", f"highpass=f=80,silencedetect=noise={noise_db:.1f}dB:d={min_gap:.2f}",
            "-f", "null", "-",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        err = res.stderr or ""
        starts = [float(x) for x in re.findall(r"silence_start:\s*(-?[\d\.]+)", err)]
        ends = [float(x) for x in re.findall(r"silence_end:\s*([\d\.]+)", err)]
        if len(ends) < len(starts):
            ends.extend([float("inf")] * (len(starts) - len(ends)))
        return [(max(0.0, s), e) for s, e in zip(starts, ends)]
    except Exception as e:
        logger.debug(f"silencedetect fallback failed: {e}")
        return []


def compute_silence_edl(
    words: List[Dict[str, Any]],
    duration: float,
    mode: str = "natural",
    video_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Computes keep/delete ranges for dead-air removal with adaptive natural breath preservation
    and returns word timestamps re-timed onto the edited timeline.
    """
    clean_mode = (mode or "off").lower().strip()
    if clean_mode not in SILENCE_CUT_PRESETS:
        return {
            "mode": "off",
            "source_duration": duration,
            "edited_duration": duration,
            "removed_sec": 0.0,
            "keep_ranges": [{"start": 0.0, "end": duration}],
            "delete_ranges": [],
            "retimed_words": words or [],
        }

    cfg = SILENCE_CUT_PRESETS[clean_mode]
    min_gap = cfg["gap"]
    head_pad = cfg["head_pad"]
    tail_pad = cfg["tail_pad"]
    noise_db = cfg["noise_db"]

    delete_candidates: List[Tuple[float, float, str]] = []
    sorted_words = sorted(
        [w for w in (words or []) if w.get("word") and float(w.get("end", 0)) > float(w.get("start", 0))],
        key=lambda x: float(x.get("start", 0.0)),
    )

    if sorted_words:
        first_start = float(sorted_words[0]["start"])
        last_end = float(sorted_words[-1]["end"])

        # Trim opening dead air so voice lands within <= 0.12s (retention hook)
        head_end = first_start - head_pad
        if head_end > 0.08:
            delete_candidates.append((0.0, head_end, "head_dead_air"))

        # Trim trailing dead air after final word
        tail_start = last_end + tail_pad
        if duration - tail_start > 0.15:
            delete_candidates.append((tail_start, duration, "tail_dead_air"))

        # Trim long inter-word pauses while preserving contextual natural breath
        for i in range(1, len(sorted_words)):
            prev_w = sorted_words[i - 1]
            next_w = sorted_words[i]
            prev_end = float(prev_w["end"])
            next_start = float(next_w["start"])
            gap = next_start - prev_end
            if gap < min_gap:
                continue

            prev_txt = str(prev_w.get("word", "")).strip()
            sentence_break = bool(re.search(r"[.!?]$", prev_txt))
            keep_breath = 0.24 if gap >= 2.0 else (0.20 if sentence_break else 0.14)
            del_start = prev_end + keep_breath * 0.55
            del_end = next_start - keep_breath * 0.45
            if del_end - del_start >= 0.10:
                delete_candidates.append((del_start, del_end, f"pause_{gap:.2f}s"))
    elif video_path and os.path.exists(video_path):
        # Fallback to acoustic silence detection when transcript words are unavailable
        silences = _detect_audio_silences(video_path, noise_db=noise_db, min_gap=min_gap)
        for s_start, s_end in silences:
            clamped_end = min(duration, s_end)
            if s_start <= 0.05:
                del_s, del_e = 0.0, max(0.0, clamped_end - head_pad)
            elif clamped_end >= duration - 0.05:
                del_s, del_e = min(duration, s_start + tail_pad), duration
            else:
                del_s, del_e = s_start + 0.10, clamped_end - 0.08
            if del_e - del_s >= 0.12:
                delete_candidates.append((del_s, del_e, "acoustic_silence"))

    merged_deletes = _merge_ranges(delete_candidates)

    # Complement of deleted ranges -> kept ranges
    keep_ranges: List[Dict[str, float]] = []
    cursor = 0.0
    for d in merged_deletes:
        d_start = max(0.0, min(duration, d["start"]))
        d_end = max(0.0, min(duration, d["end"]))
        if d_start - cursor >= 0.05:
            keep_ranges.append({"start": round(cursor, 3), "end": round(d_start, 3)})
        cursor = max(cursor, d_end)
    if duration - cursor >= 0.05:
        keep_ranges.append({"start": round(cursor, 3), "end": round(duration, 3)})

    if not keep_ranges:
        keep_ranges = [{"start": 0.0, "end": round(duration, 3)}]
        merged_deletes = []

    removed_sec = sum(max(0.0, min(duration, d["end"]) - max(0.0, min(duration, d["start"]))) for d in merged_deletes)
    edited_duration = max(0.5, sum(r["end"] - r["start"] for r in keep_ranges))

    def _removed_before(t: float) -> float:
        acc = 0.0
        for d in merged_deletes:
            if d["end"] <= t:
                acc += d["end"] - d["start"]
            elif d["start"] < t:
                acc += t - d["start"]
            else:
                break
        return acc

    retimed_words: List[Dict[str, Any]] = []
    for w in sorted_words:
        w_s = float(w["start"])
        w_e = float(w["end"])
        new_s = max(0.0, round(w_s - _removed_before(w_s), 3))
        new_e = max(new_s + 0.08, round(w_e - _removed_before(w_e), 3))
        retimed_words.append({
            **w,
            "start": new_s,
            "end": min(round(edited_duration, 3), new_e),
        })

    return {
        "mode": clean_mode,
        "source_duration": round(duration, 3),
        "edited_duration": round(edited_duration, 3),
        "removed_sec": round(removed_sec, 3),
        "keep_ranges": keep_ranges,
        "delete_ranges": merged_deletes,
        "retimed_words": retimed_words,
    }


def apply_silence_cut(
    video_path: str,
    output_path: str,
    words: List[Dict[str, Any]],
    duration: float,
    mode: str = "natural",
) -> Dict[str, Any]:
    """
    Executes a single-pass A/V-synced FFmpeg trim+concat cut with 5ms micro-audio-fades
    at every join to prevent audio clicks/pops, returning the cut path and re-timed words.
    """
    clean_mode = (mode or "off").lower().strip()
    if clean_mode == "off" or clean_mode not in SILENCE_CUT_PRESETS:
        return {
            "applied": False,
            "video_path": video_path,
            "words": words or [],
            "duration": duration,
            "removed_sec": 0.0,
            "cuts_count": 0,
        }

    actual_dur = _probe_media_duration(video_path, fallback=duration)
    edl = compute_silence_edl(words=words, duration=actual_dur, mode=clean_mode, video_path=video_path)
    keep_ranges = edl["keep_ranges"]
    removed_sec = edl["removed_sec"]

    # Skip unnecessary re-encode if negligible silence found or too many micro-fragments
    if removed_sec < 0.25 or len(keep_ranges) == 0 or len(keep_ranges) > 90:
        return {
            "applied": False,
            "video_path": video_path,
            "words": words or [],
            "duration": actual_dur,
            "removed_sec": 0.0,
            "cuts_count": 0,
        }

    # Check if input has audio
    has_audio = True
    try:
        probe_a = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(video_path)],
            capture_output=True, text=True, timeout=6
        )
        has_audio = bool(probe_a.stdout and probe_a.stdout.strip())
    except Exception:
        has_audio = True

    lines: List[str] = []
    for idx, seg in enumerate(keep_ranges):
        s = seg["start"]
        e = seg["end"]
        seg_len = max(0.05, e - s)
        lines.append(f"[0:v]trim=start={s:.3f}:end={e:.3f},setpts=PTS-STARTPTS[v{idx}];")
        if has_audio:
            # 5ms micro-fade at every cut boundary prevents clicks and pops
            if seg_len > 0.03:
                fade_out_st = max(0.0, seg_len - 0.005)
                lines.append(
                    f"[0:a]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS,"
                    f"afade=t=in:d=0.005,afade=t=out:st={fade_out_st:.3f}:d=0.005[a{idx}];"
                )
            else:
                lines.append(f"[0:a]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS[a{idx}];")

    if has_audio:
        concat_in = "".join(f"[v{i}][a{i}]" for i in range(len(keep_ranges)))
        lines.append(f"{concat_in}concat=n={len(keep_ranges)}:v=1:a=1[v_out][a_out]")
    else:
        concat_in = "".join(f"[v{i}]" for i in range(len(keep_ranges)))
        lines.append(f"{concat_in}concat=n={len(keep_ranges)}:v=1:a=0[v_out]")

    filter_graph = "\n".join(lines)
    script_path = None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".silence.txt", delete=False, encoding="utf-8") as tf:
            tf.write(filter_graph)
            script_path = tf.name

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(video_path),
            "-filter_complex_script", script_path,
            "-map", "[v_out]",
        ]
        if has_audio:
            cmd.extend(["-map", "[a_out]", "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k"])
        cmd.extend([
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "17",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            str(output_path),
        ])

        timeout_sec = max(60, min(600, int(actual_dur * 4) + 60))
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec)
        if res.returncode == 0 and os.path.exists(output_path) and is_valid_mp4(output_path):
            new_dur = _probe_media_duration(output_path, fallback=edl["edited_duration"])
            logger.info(
                f"Smart Silence Jumpcut ({clean_mode}): trimmed {removed_sec:.2f}s across "
                f"{len(edl['delete_ranges'])} pause(s) ({actual_dur:.2f}s -> {new_dur:.2f}s)."
            )
            return {
                "applied": True,
                "video_path": str(output_path),
                "words": edl["retimed_words"],
                "duration": new_dur,
                "removed_sec": removed_sec,
                "cuts_count": len(edl["delete_ranges"]),
            }
        else:
            logger.warning(f"Silence cutter FFmpeg returned code {res.returncode}: {(res.stderr or '')[:220]}")
    except Exception as e:
        logger.warning(f"Silence cutter fallback to original clip: {e}")
    finally:
        if script_path and os.path.exists(script_path):
            try:
                os.unlink(script_path)
            except Exception:
                pass

    return {
        "applied": False,
        "video_path": video_path,
        "words": words or [],
        "duration": actual_dur,
        "removed_sec": 0.0,
        "cuts_count": 0,
    }
