# Obsidian Whisper

Obsidian Whisper is a tool that helps you transcribe audio recordings and convert them into well-structured notes in Markdown format suitable for use with the Obsidian note-taking application. It utilizes OpenAI's GPT models for transcription and provides options for summarizing the content with GPT.

## Getting Started

Follow these instructions to set up and use Obsidian Whisper.

### Prerequisites

- Python 3.8.x to 3.11.x
- Obsidian vault should be created with recorded audio files in the root vault directory
- FFMPEG installed and added to the system's PATH
- OpenAI API key (if you plan to use GPT for summarization)

### Installation

1. Clone this repository to your local machine:

   ```
   git clone https://github.com/your_username/obsidian-whisper.git
   ```

2. Navigate to the project folder:

   ```
   cd obsidian-whisper
   ```

3. Install the required Python packages using pip:

   ```
   run.py
   ```

### Configuration

Before running Obsidian Whisper, you need to configure it during the setup, settings may be updated anytime by running `setup.py`. 

### Usage

To transcribe and summarize audio recordings using Obsidian Whisper, follow these steps:

1. Place your audio recordings (in `.mp3` or `.webm` format) in the Obsidian Vault folder in use (Audio recorded in the Obsidian application will do this automatically).

2. Open a terminal and navigate to the project folder:

   ```
   cd obsidian-whisper
   ```

3. Run the appropriate script based on your needs:
   - For the version **with GPT summary**:
     ```
     python obsidian_whisper_summary.py
     ```
   - For the version **without GPT summary**:
     ```
     python obsidian_whisper_basic.py
     ```

4. Follow the on-screen prompts to select the Obsidian Vault folder and other options.

5. Obsidian Whisper will process the audio recordings, transcribe them, and generate Markdown notes.

6. The generated notes will be placed in the appropriate folders within your Obsidian Vault.

## License

This project is licensed under the terms of the GNU General Public License, version 3 (GPL-3.0). You may obtain a copy of the license [here](https://www.gnu.org/licenses/gpl-3.0.en.html).