import os
import subprocess
import json
import sys

VIDEO_EXTENSIONS = (
    '.mp4', '.mov', '.mkv', '.avi', '.flv', '.wmv', '.webm', '.m4v'
)

def is_video_file(filename):
    return filename.lower().endswith(VIDEO_EXTENSIONS)

def ffprobe_file(filepath):
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        filepath
    ]

    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        return json.loads(output)
    except Exception as e:
        print(f"ffprobe failed for {filepath}: {e}", file=sys.stderr)
        return None

def scan_directory(base_dir):
    results = {}
    base_dir = os.path.abspath(base_dir)

    for root, dirs, files in os.walk(base_dir):
        for filename in files:
            if is_video_file(filename):
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, base_dir)
                data = ffprobe_file(full_path)
                if data:
                    results[rel_path] = data

    return results
