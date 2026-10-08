# generate_process.py
import os
import time
import subprocess
from text_to_audio import text_to_speech_file

DONE_FILE = "done.txt"
UPLOAD_FOLDER = "user_uploads"
REELS_FOLDER = "static/reels"

# Ensure done.txt exists
if not os.path.exists(DONE_FILE):
    open(DONE_FILE, "w").close()

# Ensure reels folder exists
os.makedirs(REELS_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def text_to_audio(folder):
    """Generate audio.mp3 from desc.txt using UTF-8 encoding."""
    print("TTA -", folder)
    desc_path = os.path.join(UPLOAD_FOLDER, folder, "desc.txt")
    
    if not os.path.exists(desc_path):
        print(f"⚠️ desc.txt not found in {folder}, skipping...")
        return False

    with open(desc_path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    if not text:
        print(f"⚠️ desc.txt in {folder} is empty, skipping...")
        return False

    print(f"Text to convert: {text}")
    try:
        text_to_speech_file(text, folder)
        print(f"✅ Audio generated for {folder}")
        return True
    except Exception as e:
        print(f"❌ Failed to generate audio for {folder}: {e}")
        return False


def create_reel(folder):
    """Combine images and audio into a vertical reel using FFmpeg."""
    input_txt = os.path.join(UPLOAD_FOLDER, folder, "input.txt")
    audio_file = os.path.join(UPLOAD_FOLDER, folder, "audio.mp3")
    output_file = os.path.join(REELS_FOLDER, f"{folder}.mp4")

    if not os.path.exists(input_txt):
        print(f"⚠️ input.txt not found in {folder}, skipping reel creation...")
        return
    if not os.path.exists(audio_file):
        print(f"⚠️ audio.mp3 not found in {folder}, skipping reel creation...")
        return

    command = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", input_txt,
        "-i", audio_file,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        "-r", "30",
        "-pix_fmt", "yuv420p",
        output_file
    ]

    try:
        subprocess.run(command, check=True)
        print(f"🎬 Reel created for {folder}")
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg failed for {folder}: {e}")


if __name__ == "__main__":
    while True:
        print("Processing queue...")
        
        # Read processed folders
        with open(DONE_FILE, "r") as f:
            done_folders = [line.strip() for line in f.readlines()]

        # Get all subfolders in user_uploads
        folders = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isdir(os.path.join(UPLOAD_FOLDER, f))]

        for folder in folders:
            if folder not in done_folders:
                print(f"🆕 Found new folder: {folder}")

                if text_to_audio(folder):
                    create_reel(folder)
                    # Mark folder as done
                    with open(DONE_FILE, "a") as f:
                        f.write(folder + "\n")
                else:
                    print(f"⚠️ Skipping {folder} due to missing/invalid desc.txt")

        # Wait a few seconds before checking again
        time.sleep(4)
