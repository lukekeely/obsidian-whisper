import os
import json
from pydub import AudioSegment
import openai
import whisper

# Load configuration from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Configurable Parameters
OBSIDIAN_VAULTS_PATH = config.get('OBSIDIAN_VAULT_PATH')
OPENAI_API_KEY = config.get('API_KEY')
AUDIO_CHUNK_LENGTH_MS = 5 * 60 * 1000  # 5 minutes in milliseconds
WHISPER_MODEL = config.get('DEFAULT_WHISPER_SIZE')
GPT_TURBO_MODEL = config.get('DEFAULT_MODEL')
GPT_PROCESSING_TEMP = 0.5
GPT_MAX_TOKENS = 4096
GPT_TOP_P = 1
GPT_FREQ_PENALTY = 0
GPT_PRESENCE_PENALTY = 0

# OpenAI Messages
GPT_PROCESSING_PROMPT = {
    "role": "system",
    "content": "You are a theoretical physics professor. Convert the following lecture transcription into well-structured notes with a focus on mathematics and equations, in markdown format suitable for Obsidian."
}
GPT_CATEGORIZATION_PROMPT = "Given the following summary, categorize it into one of these folders: {}. Also, give a short name for the markdown file based on the content.\n\nSummary:\n{}\n\nFolders: {}\n\nSuggested Category and Filename. Return only in format: '[Category], [Title]' "

# Function Definitions
def split_audio(file_path, chunk_length_ms=AUDIO_CHUNK_LENGTH_MS):
    audio = AudioSegment.from_file(file_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
    return chunks

def transcribe_audio(file_path):
    try:
        model = whisper.load_model(WHISPER_MODEL)
        result = model.transcribe(file_path)
        return result["text"]
    except Exception as e:
        print(f"Error in transcribing audio: {e}")
        return ""

def process_transcription(text):
    try:
        openai.api_key = OPENAI_API_KEY
        messages = [
            GPT_PROCESSING_PROMPT,
            {"role": "user", "content": text}
        ]
        response = openai.ChatCompletion.create(
            model=GPT_TURBO_MODEL,
            messages=messages,
            temperature=GPT_PROCESSING_TEMP,
            max_tokens=GPT_MAX_TOKENS,
            top_p=GPT_TOP_P,
            frequency_penalty=GPT_FREQ_PENALTY,
            presence_penalty=GPT_PRESENCE_PENALTY
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print(f"Error in processing transcription: {e}")
        return ""

def save_to_markdown(folder, filename, content, is_summary=False):
    markdown_folder = os.path.join(folder, "Transcripts" if not is_summary else "")
    os.makedirs(markdown_folder, exist_ok=True)
    with open(os.path.join(markdown_folder, filename + ".md"), "w", encoding='utf-8') as f:
        content = content.replace("```markdown", "").replace("```", "") if is_summary else content
        f.write(content)

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

def categorize_and_name(summary, allowed_categories):
    try:
        openai.api_key = OPENAI_API_KEY
        formatted_prompt = GPT_CATEGORIZATION_PROMPT.format(", ".join(allowed_categories), summary, ", ".join(allowed_categories))
        messages = [
            {"role": "user", "content": formatted_prompt}
        ]
        response = openai.ChatCompletion.create(
            model=GPT_TURBO_MODEL,
            messages=messages,
            temperature=GPT_PROCESSING_TEMP,
            max_tokens=GPT_MAX_TOKENS,
            top_p=GPT_TOP_P,
            frequency_penalty=GPT_FREQ_PENALTY,
            presence_penalty=GPT_PRESENCE_PENALTY
        )
        output = response.choices[0].message["content"].strip()
        output_lines = output.split(', ')
        if len(output_lines) >= 2:
            suggested_category = output_lines[0]
            filename = output_lines[1]
            category = suggested_category if suggested_category in allowed_categories else "Uncategorized"
            return category, filename
        else:
            return "Uncategorized", "Untitled"
    except Exception as e:
        print(f"Error in categorizing and naming: {e}")
        return "Uncategorized", "Untitled"

def unique_filename(folder, filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    unique_filename = filename
    while os.path.exists(os.path.join(folder, unique_filename)):
        unique_filename = f"{base}_{counter}{ext}"
        counter += 1
    return unique_filename

def main():
    vaults = os.listdir(OBSIDIAN_VAULTS_PATH)
    print("Available Vaults:")
    for i, vault in enumerate(vaults):
        print(f"{i}: {vault}")

    selected_vault_index = int(input("Select a vault by index: "))
    selected_vault = vaults[selected_vault_index]
    vault_folder = os.path.join(OBSIDIAN_VAULTS_PATH, selected_vault)

    allowed_categories = [f for f in os.listdir(vault_folder) if os.path.isdir(os.path.join(vault_folder, f))]

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

            processed_transcription = process_transcription(full_transcription)
            print(f"Processed transcription for {filename}:\n{processed_transcription}\n")

            category, new_filename = categorize_and_name(processed_transcription, allowed_categories)
            new_filename = unique_filename(vault_folder, new_filename)

            category_folder = os.path.join(vault_folder, category)
            os.makedirs(category_folder, exist_ok=True)

            save_to_markdown(vault_folder, new_filename, full_transcription)
            save_to_markdown(category_folder, new_filename, processed_transcription, is_summary=True)

            update_log(vault_log_path, filename)

if __name__ == "__main__":
    main()
