#!/usr/bin/env python3

import argparse
import json
import os
import subprocess
import sys

def is_video_file(filename):
    """
    A simple check for common video file extensions.
    You can expand or modify this list as needed.
    """
    VIDEO_EXTENSIONS = (
        '.mp4', '.mov', '.mkv', '.avi', '.flv', '.wmv', '.webm', '.m4v'
    )
    return filename.lower().endswith(VIDEO_EXTENSIONS)

def ffprobe_file(filepath):
    """
    Run ffprobe on a single file and return the parsed JSON.
    Returns None if ffprobe fails.
    """
    cmd = [
        "ffprobe",
        "-v", "quiet",             # Suppress standard output/errors
        "-print_format", "json",   # Output in JSON format
        "-show_format",
        "-show_streams",
        filepath
    ]

    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        return json.loads(output)
    except subprocess.CalledProcessError as e:
        # ffprobe returned an error (e.g. not a valid media file)
        print(f"Warning: ffprobe failed for '{filepath}'. Skipping.", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        # Output was not valid JSON
        print(f"Warning: Could not decode ffprobe JSON for '{filepath}'. Skipping.", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(
        description="Recursively run ffprobe on video files and produce a JSON index keyed by relative paths."
    )
    parser.add_argument(
        "directory",
        help="Path to the directory to scan for video files."
    )
    parser.add_argument(
        "-o", "--output",
        default="probe_results.json",
        help="Path for the output JSON file (default: probe_results.json)."
    )
    args = parser.parse_args()

    base_dir = os.path.abspath(args.directory)
    results = {}

    # Walk through the directory tree
    for root, dirs, files in os.walk(base_dir):
        for filename in files:
            if is_video_file(filename):
                full_path = os.path.join(root, filename)
                # Compute the relative path from the base directory
                rel_path = os.path.relpath(full_path, start=base_dir)

                # Run ffprobe and store the result
                probe_data = ffprobe_file(full_path)
                if probe_data is not None:
                    results[rel_path] = probe_data

    # Write the accumulated results to JSON
    with open(args.output, 'w', encoding='utf-8') as out_file:
        json.dump(results, out_file, indent=2, ensure_ascii=False)

    print(f"Probe results saved to '{args.output}'")

if __name__ == "__main__":
    main()
