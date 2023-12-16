import subprocess
import os

def run_subprocess(file_path):
  """Runs a subprocess in the specified file path."""
  subprocess.run(f"ffmpeg -i \"data/videos/{file_path}\" -vf scale=1280:720 \"data/converted/{file_path}\"", shell=True)

for file_name in os.listdir("data/videos/"):
    if file_name.endswith(".mp4"):
        print(file_name)
        run_subprocess(file_name)
