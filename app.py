import streamlit as st
import yt_dlp
import whisper
from transformers import pipeline
import re
import os
import glob
import io
import time
import requests

@st.cache_resource
def load_models(model_size="base"):  # <-- Modified to accept model size param
    whisper_model = whisper.load_model(model_size)  # Load selected model size
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    return whisper_model, summarizer

def get_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def find_downloaded_file(basename):
    matches = glob.glob(f"{basename}.*")
    return matches[0] if matches else None

def is_valid_youtube_url(url):
    pattern = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"
    return re.match(pattern, url) is not None

def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'forceurl': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        title = info.get('title', 'Unknown Title')
        thumbnail = info.get('thumbnail', None)
        duration = info.get('duration', 0)  # duration in seconds
        return title, thumbnail, duration
    except Exception:
        return "Unknown Title", None, 0

def format_duration(seconds):
    mins, secs = divmod(seconds, 60)
    hrs, mins = divmod(mins, 60)
    if hrs > 0:
        return f"{hrs}h {mins}m {secs}s"
    else:
        return f"{mins}m {secs}s"

def download_audio(url):
    video_id = get_video_id(url)
    if not video_id:
        st.error("Invalid YouTube URL: unable to extract video ID.")
        return None

    basename = video_id
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',  # force m4a first, fallback to bestaudio
        'outtmpl': f"{basename}.%(ext)s",
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'geo_bypass': True,
        'retries': 3,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except yt_dlp.utils.DownloadError as e:
        st.error(f"Error downloading audio: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

    audio_file = find_downloaded_file(basename)
    if not audio_file or not os.path.exists(audio_file):
        st.error(f"Failed to find downloaded audio file starting with: {basename}")
        return None

    return audio_file

def cleanup_file(file_path):  # <-- Added cleanup helper function
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        st.warning(f"Could not delete temp file: {file_path}. Error: {e}")

def transcribe_audio(model, audio_path):
    try:
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        st.error(f"Error during transcription: {e}")
        return None

def summarize_text(summarizer, text, max_chunk=1000):
    sentences = text.split('. ')
    chunks = []
    current_chunk = ''
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_chunk:
            current_chunk += sentence + '. '
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + '. '
    if current_chunk:
        chunks.append(current_chunk.strip())

    summaries = []
    for chunk in chunks:
        summary = summarizer(chunk, max_length=150, min_length=40, do_sample=False)[0]['summary_text']
        summaries.append(summary)
    return ' '.join(summaries)

def save_feedback(name, email, feedback):
    # Replace with your actual Formspree endpoint
    formspree_url = "https://formspree.io/f/mrblrrgb"  
    data = {
        "name": name,
        "email": email,
        "message": feedback
    }
    try:
        response = requests.post(formspree_url, data=data)
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception:
        return False

def main():
    st.title("YouTube Audio Summarizer 🎧")

    st.markdown(
        "<div style='background-color:#fffae6; padding:10px; border-left:6px solid #f9a825; margin-bottom:20px;'>"
        "<strong>🚀 New updates coming soon! Stay tuned.</strong>"
        "</div>",
        unsafe_allow_html=True
    )

    # Sidebar with instructions and model selection -- Added model selection dropdown
    st.sidebar.header("Instructions")
    st.sidebar.markdown("""
    - Enter a valid YouTube video URL.
    - The app downloads the audio, transcribes it then summarizes it.
    - Videos longer than 1 hour may not work well.
    - Use the **Clear** button to reset the input and outputs.
    - Download your transcript and summary as TXT files after summarization.
    """)

    model_option = st.sidebar.selectbox(
        "Select Whisper Model Size:",
        ("tiny", "base", "medium", "large"),
        index=1
    )



    st.sidebar.header("Feedback")
    name = st.sidebar.text_input("Your Name (optional)")
    email = st.sidebar.text_input("Your Email (optional)")
    feedback = st.sidebar.text_area("Your Feedback", key="feedback")
    if st.sidebar.button("Submit Feedback"):
        if feedback.strip() == "":
            st.sidebar.warning("Please enter your feedback before submitting.")
        else:
            if save_feedback(name, email, feedback):
                st.sidebar.success("✅ Thank you for your feedback!")
            else:
                st.sidebar.error("❌ Failed to send feedback. Please try again later.")

    # Initialize cache dict for transcripts and summaries per URL -- Added cache dict
    if "cache" not in st.session_state:
        st.session_state.cache = {}

    # Initialize session_state variables if not present
    for key in ['url', 'transcript', 'summary']:
        if key not in st.session_state:
            st.session_state[key] = ''

    url = st.text_input("Enter YouTube URL:", value=st.session_state.url)

    if url:
        title, thumbnail, duration = get_video_info(url)
        st.markdown(f"### {title}")
        if thumbnail:
            st.image(thumbnail, width=400)
        if duration:
            st.markdown(f"**Duration:** {format_duration(duration)}")

        if duration > 3600:
            st.warning("⚠️ Video is longer than 1 hour, please try a shorter video.")
            return

    if st.button("Clear"):
        st.session_state.url = ''
        st.session_state.transcript = ''
        st.session_state.summary = ''

    if st.button("Summarize"):
        st.session_state.url = url  # Save current input

        if not url:
            st.warning("Please enter a YouTube URL.")
            return

        if not is_valid_youtube_url(url):
            st.warning("Please enter a valid YouTube URL.")
            return

        # Check cache before processing -- Added caching logic
        if url in st.session_state.cache:
            transcript, summary = st.session_state.cache[url]
            st.session_state.transcript = transcript
            st.session_state.summary = summary
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                status_text.text("Downloading audio...")
                audio_path = download_audio(url)
                if audio_path is None:
                    return
                progress_bar.progress(33)

                whisper_model, summarizer = load_models(model_option)

                status_text.text("Transcribing audio...")
                transcript = transcribe_audio(whisper_model, audio_path)
                if transcript is None or transcript.strip() == '':
                    st.error("Transcription returned empty result. Try another video.")
                    cleanup_file(audio_path)  # cleanup on error
                    return
                progress_bar.progress(66)

                status_text.text("Summarizing transcript...")
                summary = summarize_text(summarizer, transcript)
                progress_bar.progress(100)

                # Save results in session state and cache
                st.session_state.transcript = transcript
                st.session_state.summary = summary
                st.session_state.cache[url] = (transcript, summary)

                cleanup_file(audio_path)  # <-- Delete audio file after processing
                status_text.text("Done!")
            except Exception as e:
                st.error(f"An error occurred: {e}")
                if 'audio_path' in locals():
                    cleanup_file(audio_path)
                return

    # Show results from session_state if available
    if st.session_state.transcript:
        st.subheader("Transcript")
        st.write(st.session_state.transcript)
        st.download_button(
            label="Download Transcript as TXT",
            data=st.session_state.transcript.encode('utf-8'),
            file_name="transcript.txt",
            mime="text/plain"
        )

    if st.session_state.summary:
        st.subheader("Summary")
        st.write(st.session_state.summary)
        st.download_button(
            label="Download Summary as TXT",
            data=st.session_state.summary.encode('utf-8'),
            file_name="summary.txt",
            mime="text/plain"
        )

    st.markdown("---")  # A horizontal separator line
    st.markdown(
        "<div style='background-color:#fffae6; padding:10px; border-left:6px solid #f9a825; margin-top:20px;'>"
        "<strong>🚀 New updates coming soon! Stay tuned.</strong>"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
