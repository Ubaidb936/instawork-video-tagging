import os
import subprocess
import tempfile
import urllib.request


def download_video(url: str, dest_path: str):
    urllib.request.urlretrieve(url, dest_path)


def extract_frames(video_path: str, num_frames: int = 8) -> list[str]:
    """Extract evenly spaced frames from video, return list of image file paths."""
    out_dir = tempfile.mkdtemp()
    duration = get_duration(video_path)
    interval = max(duration / num_frames, 1)

    subprocess.run([
        "ffmpeg", "-i", video_path,
        "-vf", f"fps=1/{interval:.2f}",
        "-vframes", str(num_frames),
        "-q:v", "2",
        f"{out_dir}/frame_%03d.jpg"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    frames = sorted([
        os.path.join(out_dir, f)
        for f in os.listdir(out_dir)
        if f.endswith(".jpg")
    ])
    return frames


def extract_audio(video_path: str) -> str:
    """Extract audio track to a temp mp3 file, return path."""
    out_path = tempfile.mktemp(suffix=".mp3")
    subprocess.run([
        "ffmpeg", "-i", video_path,
        "-q:a", "0", "-map", "a",
        out_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return out_path


def get_duration(video_path: str) -> float:
    """Return video duration in seconds using ffprobe."""
    result = subprocess.run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ], capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 60.0
