import os
import json
from pydub import AudioSegment
import whisper

# Load configuration from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)
    
# Configurable Parameters
OBSIDIAN_VAULTS_PATH = config.get('OBSIDIAN_VAULT_PATH')
AUDIO_CHUNK_LENGTH_MS = 5 * 60 * 1000  # 5 minutes in milliseconds
WHISPER_MODEL = config.get('DEFAULT_WHISPER_SIZE')

# Split audio into chunks
def split_audio(file_path, chunk_length_ms=AUDIO_CHUNK_LENGTH_MS):
    audio = AudioSegment.from_file(file_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
    return chunks

# Transcribe audio using Whisper
def transcribe_audio(file_path):
    try:
        model = whisper.load_model(WHISPER_MODEL)
        result = model.transcribe(file_path)
        return result["text"]
    except Exception as e:
        print(f"Error in transcribing audio: {e}")
        return ""

# Save transcription to a Markdown file
def save_to_markdown(folder, filename, content):
    markdown_folder = os.path.join(folder, "Transcripts")
    os.makedirs(markdown_folder, exist_ok=True)
    with open(os.path.join(markdown_folder, filename + ".md"), "w", encoding='utf-8') as f:
        f.write(content)

# Update transcription log
def update_log(log_path, filename):
    try:
        log_data = []
        if os.path.exists(log_path):
            with open(log_path, "r") as log_file:
                log_data = json.load(log_file)
        log_data.append(filename)
        with open(log_path, "w") as log_file:
            json.dump(log_data, log_file, indent=4)
    except Exception as e:
        print(f"Error updating log: {e}")

# Check if a file has already been processed
def already_processed(log_path, filename):
    try:
        if os.path.exists(log_path):
            with open(log_path, "r") as log_file:
                log_data = json.load(log_file)
            return filename in log_data
        return False
    except Exception as e:
        print(f"Error checking processed files: {e}")
        return False

def main():
    vaults = os.listdir(OBSIDIAN_VAULTS_PATH)
    print("Available Vaults:")
    for i, vault in enumerate(vaults):
        print(f"{i}: {vault}")

    selected_vault_index = int(input("Select a vault by index: "))
    selected_vault = vaults[selected_vault_index]
    vault_folder = os.path.join(OBSIDIAN_VAULTS_PATH, selected_vault)

    audio_files = [f for f in os.listdir(vault_folder) if f.endswith(".mp3") or f.endswith(".webm")]
    if not audio_files:
        print("No audio recordings found in the selected vault.")
        return

    vault_log_path = os.path.join(vault_folder, "transcription_log.json")

    print(f"Processing audio recordings in '{selected_vault}' vault...\n")

    for filename in audio_files:
        if not already_processed(vault_log_path, filename):
            file_path = os.path.join(vault_folder, filename)
            print(f"Processing {filename}...")

            audio_chunks = split_audio(file_path)
            full_transcription = ""

            for i, chunk in enumerate(audio_chunks):
                chunk_path = f"temp_chunk_{i}.mp3"
                chunk.export(chunk_path, format="mp3")

                transcription = transcribe_audio(chunk_path)
                full_transcription += transcription + " "
                os.remove(chunk_path)

            print(f"Transcription for {filename} done.")
            base_filename = os.path.splitext(filename)[0]
            save_to_markdown(vault_folder, base_filename, full_transcription)
            update_log(vault_log_path, filename)

if __name__ == "__main__":
    main()
