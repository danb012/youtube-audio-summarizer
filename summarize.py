from transformers import pipeline
from pathlib import Path

def chunk_text(text, max_chunk=1000):
    # Split text into chunks of max_chunk tokens (approx chars here)
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
    return chunks

def summarize_text(text):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    chunks = chunk_text(text)
    summaries = []
    for i, chunk in enumerate(chunks):
        print(f"Summarizing chunk {i+1}/{len(chunks)}...")
        summary = summarizer(chunk, max_length=150, min_length=40, do_sample=False)[0]['summary_text']
        summaries.append(summary)
    return ' '.join(summaries)

if __name__ == "__main__":
    transcript_path = Path("download.txt")
    summary_path = Path("summary.txt")

    if not transcript_path.exists():
        print(f"Transcript file {transcript_path} not found! Run transcription first.")
        exit(1)

    text = transcript_path.read_text(encoding="utf-8")
    summary = summarize_text(text)

    summary_path.write_text(summary, encoding="utf-8")
    print(f"Summary saved to {summary_path}")
    print("\n=== Summary Preview ===")
    print(summary)
