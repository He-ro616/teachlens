# backend/transcriber.py
import os
import ffmpeg
import tempfile
from transformers import pipeline

# Initialize the Hugging Face Whisper pipeline once
speech_recognizer = pipeline("automatic-speech-recognition", model="openai/whisper-base")

def extract_audio_from_video(video_path: str, audio_out_path: str):
    """
    Extract mono 16kHz WAV audio from video using ffmpeg-python.
    """
    (
        ffmpeg
        .input(video_path)
        .output(audio_out_path, ac=1, ar=16000, format='wav')
        .overwrite_output()
        .run(quiet=True)
    )
    return audio_out_path

def transcribe_audio_from_video(video_path: str, uid: str = None, temp_dir: str = None):
    """
    Full pipeline: extract audio → transcribe → return transcript & audio path.
    """
    if temp_dir is None:
        temp_dir = tempfile.mkdtemp()

    if uid is None:
        uid = "temp"

    audio_path = os.path.join(temp_dir, f"{uid}.wav")

    # 1️⃣ Extract audio
    extract_audio_from_video(video_path, audio_path)

    # 2️⃣ Transcribe using Hugging Face Whisper
    result = speech_recognizer(audio_path)
    transcript = result.get("text", "")

    return transcript, audio_path
