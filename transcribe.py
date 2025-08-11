import whisper
from pathlib import Path

def transcribe(audio_path):
    print(f"Loading Whisper model...")
    model = whisper.load_model("base")  # change model size if you want (tiny, small, medium, large)
    print(f"Transcribing audio: {audio_path}")
    result = model.transcribe(audio_path)
    transcript_text = result["text"]
    print(f"Saving transcript to file...")
    out_path = Path(audio_path).with_suffix(".txt")
    out_path.write_text(transcript_text, encoding="utf-8")
    print(f"Transcription complete! Transcript saved at {out_path}")

if __name__ == "__main__":
    audio_file = "download.mp3"
    transcribe(audio_file)
