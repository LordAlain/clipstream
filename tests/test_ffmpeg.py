import unittest
from tasks.tasks import generate_hls, start_hls_conversion
import requests
import os

def download_video(url, save_path):
    """
    Download a video from a URL and save it to the specified path.
    :param url: URL of the video to download
    :param save_path: Path to save the downloaded video
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for HTTP errors

        # Ensure the directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Write the content to the file in chunks
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"Video downloaded successfully: {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download video: {e}")
        raise

# Usage
video_url = "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_30mb.mp4"
output_path = "media/test_video.mp4"



class TestFFmpegHLSGeneration(unittest.TestCase):
    def setUp(self):
        """
        Set up test environment. This method runs before each test.
        """
        self.video_path = "media/test_video.mp4"
        self.output_dir = "media/hls_output"

        # print("FFMPEG - Environment variables:")
        # for key, value in os.environ.items():
        #     print(f"{key}: {value}")

        # Ensure test_video.mp4 exists
        if not os.path.exists(self.video_path):
            # with open(self.video_path, "wb") as f:
            #     f.write(b"\x00" * 1024)  # Create a dummy video file
            download_video(video_url, output_path)

    def test_generate_hls(self):
        """
        Test the HLS generation task.
        """
        try:
            result = generate_hls(self.video_path, self.output_dir)
            self.assertTrue(os.path.exists(result), f"HLS file not found: {result}")
            print(f"Test passed. HLS generated at {result}")
        except Exception as e:
            self.fail(f"HLS generation failed with error: {e}")

    def tearDown(self):
        """
        Clean up after tests. This method runs after each test.
        """
        # if os.path.exists(self.video_path):
        #     os.remove(self.video_path)

        if os.path.exists(self.output_dir):
            for root, dirs, files in os.walk(self.output_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(self.output_dir)

class TestHLSConversion(unittest.TestCase):
    def test_hls_conversion(self):
        input_stream_url = "media/test_video.mp4"  # Replace with your test input
        output_dir = "media/hls_test"

        try:
            result = start_hls_conversion(input_stream_url, output_dir)
            playlist_path = os.path.join(output_dir, "playlist.m3u8")
            self.assertTrue(os.path.exists(playlist_path), "HLS playlist was not generated.")
            print(result)
        except Exception as e:
            self.fail(f"HLS conversion task failed with error: {e}")

if __name__ == "__main__":
    unittest.main()
