import argparse
import os
import subprocess


def convert_videos(input_dir: str, output_dir: str) -> None:
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".mp4"):
                input_path = os.path.join(root, file)
                relative_path = os.path.relpath(input_path, input_dir)
                output_path = os.path.join(output_dir, relative_path)

                output_dir_path = os.path.dirname(output_path)
                if not os.path.exists(output_dir_path):
                    os.makedirs(output_dir_path)

                command = [
                    "ffmpeg", "-y", "-i", input_path,
                    "-c:v", "h264_nvenc", "-preset", "slow", "-profile:v", "main",
                    "-cq:v", "31", "-c:a", "aac", "-b:a", "128k", "-ac", "2",
                    "-vf", "yadif=0:-1:0,scale=1920:1080",
                    "-movflags", "+faststart", output_path,
                ]

                print(f"Processing {input_path} to {output_path}")
                subprocess.run(command, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert videos using FFmpeg.")
    parser.add_argument("input_directory", type=str, help="Path to the input directory.")
    parser.add_argument("output_directory", type=str, help="Path to the output directory.")

    args = parser.parse_args()
    convert_videos(args.input_directory, args.output_directory)
