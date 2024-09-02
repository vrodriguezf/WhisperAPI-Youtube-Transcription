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

if len(sys.argv) < 2:
    print("Error: YouTube link not provided.")
    sys.exit(1)

youtube_link = sys.argv[1]

audio_file = youtube_preprocess(youtube_link)

no_of_chunks = chunk_by_size(audio_file)

for i in range(no_of_chunks):
    print(f"process_chunks/chunk{i}.wav")
    curr_file = open(f"process_chunks/chunk{i}.wav", "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=curr_file
    )

    with open("videotext.txt", "a") as f:
        f.write(transcript.text)

# Remove stuff
shutil.rmtree("process_chunks")
os.remove(audio_file)