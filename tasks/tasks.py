import subprocess
import os
from celery import shared_task
from pathlib import Path

@shared_task
def add(x, y):
    print(f"Executing add({x} + {y})")
    return x + y


@shared_task
def generate_hls(video_path, output_dir):
    """
    Converts a video file to HLS format.
    Args:
        video_path (str): Path to the input video file.
        output_dir (str): Directory to save HLS files.
    Returns:
        str: Path to the generated .m3u8 file.
    """
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    hls_output = output_dir_path / 'playlist.m3u8'

    command = [
        'ffmpeg',
        '-i', video_path,
        '-c:v', 'copy',
        '-start_number', '0',
        '-hls_time', '10',
        '-hls_list_size', '0',
        '-f', 'hls',
        str(hls_output)
    ]

    # subprocess.run(command, check=True)
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg failed: {e}")

    return str(hls_output)

@shared_task
def start_hls_conversion(input_stream_url, output_dir):
    """
    Convert incoming video streams to HLS segments using FFmpeg.
    :param input_stream_url: URL of the incoming livestream (e.g., RTMP stream)
    :param output_dir: Directory to store the HLS `.m3u8` and `.ts` files
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    hls_playlist = os.path.join(output_dir, "playlist.m3u8")

    # FFmpeg command for HLS conversion
    command = [
        "ffmpeg",
        "-i", input_stream_url,
        "-c:v", "copy",
        "-c:a", "aac",
        "-f", "hls",
        "-hls_time", "6",  # 6-second segments
        "-hls_list_size", "0",  # Include all segments in the playlist
        "-hls_segment_filename", os.path.join(output_dir, "segment_%03d.ts"),
        hls_playlist
    ]

    try:
        subprocess.run(command, check=True)
        return f"HLS stream started at {hls_playlist}"
    except subprocess.CalledProcessError as e:
        raise Exception(f"FFmpeg failed with error: {e}")