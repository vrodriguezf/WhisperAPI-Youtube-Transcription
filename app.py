from fasthtml.common import *
from openai import OpenAI
import os
import sys
import shutil
from videoproc import youtube_preprocess
from chunking import chunk_by_size

client = OpenAI()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY environment variable not found.")
    sys.exit(1)

app, rt = fast_app()

@rt('/')
def get():
    form = Form(
        Input(id="youtube_link", name="youtube_link", placeholder="Enter YouTube Link", type="text"),
        Button("Transcribe Video"),
        hx_post="/transcribe",
        hx_target="#transcription_output",
        hx_swap="innerHTML"
    )
    busy_indicator = PicoBusy()
    # Including the script directly in the HTML content
    script = """
    <script>
    function copyToClipboard() {
        var text = document.getElementById("transcription_text").innerText;
        navigator.clipboard.writeText(text).then(function() {
            alert('Copied to clipboard!');
        }, function(err) {
            alert('Failed to copy text: ', err);
        });
    }
    </script>
    """
    return Titled("YouTube Transcription", form, Div(id="transcription_output", *busy_indicator), 
                  NotStr(script), Br())

@rt('/transcribe')
def post(youtube_link:str):
    if not youtube_link:
        return P("Error: No YouTube link provided.")

    # Call the existing script logic
    audio_file = youtube_preprocess(youtube_link)
    if audio_file is None:
        return P("Error: Failed to download or process the YouTube video.")
    no_of_chunks = chunk_by_size(audio_file)

    transcript_text = ""
    for i in range(no_of_chunks):
        curr_file = open(f"process_chunks/chunk{i}.wav", "rb")
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=curr_file
        )
        transcript_text += transcript.text + "\n"

    # Clean up
    shutil.rmtree("process_chunks")
    os.remove(audio_file)

    # Write transcription to a file
    file_path = "transcription.txt"
    with open(file_path, "w") as f:
        f.write(transcript_text)

    # Add buttons for copying to clipboard and exporting to a file
    copy_button = Button("Copy to Clipboard", cls="copy-button", onclick="copyToClipboard()")
    export_link = A("Export to File", href="/download", cls="export-link", download="transcription.txt")

    # Return the transcription result with buttons
    return Div(
        H3("Transcription Result:"),
        Textarea(transcript_text, id="transcription_text", readonly=True, rows=10),
        Div(copy_button, export_link),
    )

@rt('/download')
def get():
    file_path = "transcription.txt"
    return FileResponse(file_path, filename="transcription.txt", media_type="text/plain")

@rt('/script')
def script():
    return """
    function copyToClipboard() {
        var text = document.getElementById("transcription_text").innerText;
        navigator.clipboard.writeText(text).then(function() {
            alert('Copied to clipboard!');
        }, function(err) {
            alert('Failed to copy text: ', err);
        });
    }
    """

serve()
