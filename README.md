# YouTube Audio Summarizer 🎧

A Streamlit app that downloads audio from YouTube videos, transcribes the speech using OpenAI Whisper, and provides a summarized text using Hugging Face transformers.

---

## Features

- Download and extract audio from YouTube videos  
- Transcribe audio to text with Whisper  
- Summarize long transcripts for quick insights  
- Select different Whisper model sizes for faster or more accurate transcription  
- Download transcript and summary as TXT files  
- Provide feedback directly from the app sidebar

---

**For the best experience, please run the app locally by following the instructions below.**

---

## Run Locally

### Prerequisites

- Python 3.8 or newer  
- [ffmpeg](https://ffmpeg.org/download.html) installed and added to your system PATH  
- Git (optional, for cloning)

### Setup Instructions

1. Clone this repository (or download ZIP):  
   bash
   git clone https://github.com/danb012/youtube-audio-summarizer.git
   cd youtube-audio-summarizer

(Optional) Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

Install Python dependencies:
pip install -r requirements.txt
Make sure ffmpeg is installed and accessible from your command line:
ffmpeg -version
Run the Streamlit app:
streamlit run app.py

Usage:
Paste a valid YouTube video URL in the input box.
Select the Whisper model size (smaller is faster, larger is more accurate).
Click Summarize to download, transcribe, and summarize the video audio.
View the transcript and summary on the page.
Download the transcript and summary as TXT files if needed.
Provide feedback via the sidebar form.

Limitations
Videos longer than 1 hour fail due to processing time and resource limits.
Requires stable internet to download videos and access models.
Not guaranteed to work on all operating systems or cloud platforms without proper setup.

Feedback
Your feedback is appreciated! Use the form in the sidebar to send comments or suggestions.


Acknowledgments
OpenAI Whisper for transcription
Hugging Face Transformers for summarization
yt-dlp for YouTube audio extraction
Streamlit for the app framework