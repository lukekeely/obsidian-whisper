import os
import json
import subprocess

# Define choices and default values
DEFAULT_VERSION_CHOICES = {
    "1": {"name": "obsidian_whisper_summary", "requires_gpt": True},
    "2": {"name": "obsidian_whisper_basic", "requires_gpt": False}
}

DEFAULT_MODEL_CHOICES = {
    "1": "gpt-4-turbo-preview",
    "2": "gpt-4",
    "3": "gpt-3.5-turbo-1106"
}

DEFAULT_WHISPER_SIZE_CHOICES = {
    "1": "small",
    "2": "medium",
    "3": "large"
}

# Default values
DEFAULT_MODEL = "gpt-3.5-turbo-1106"
DEFAULT_WHISPER_SIZE = "small"

# Function to install Python packages from requirements.txt
def install_requirements():
    print("Installing requirements.")
    try:
        subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
        print("Requirements installed successfully.")
    except subprocess.CalledProcessError:
        print("Failed to install requirements. Please install them manually using 'pip install -r requirements.txt'.")

# Function to check if the configuration JSON exists
def config_exists():
    return os.path.exists("config.json")

# Function to run the selected script
def run_script(script_name):
    try:
        subprocess.run(["python", script_name], check=True)
    except subprocess.CalledProcessError:
        print(f"Failed to run the script: {script_name}")

# Main setup script
if __name__ == "__main__":
    if config_exists():
        while True:
            reconfigure = input("Configuration already exists. Would you like to reconfigure (y/N)? ").strip().lower()
            if reconfigure.lower() == "y":
                break
            else:
                print("Setup complete. Exiting.")
                run_script("run.py")
                exit()

    print("Welcome to the Obsidian Whisper Setup!")

    # Get user input for Obsidian Vault path
    obsidian_vault_path = input("Enter the path to your Obsidian Vault folder: ").strip()

    # Get user input for default version choice
    print("Choose default script version:")
    for key, choice in DEFAULT_VERSION_CHOICES.items():
        print(f"{key}. {choice['name']}")

    default_version = input("Enter the number of your choice (default: 2): ").strip() or "2"
    requires_gpt = DEFAULT_VERSION_CHOICES.get(default_version, {}).get("requires_gpt", False)
    print(DEFAULT_VERSION_CHOICES.get(default_version))
    default_version = DEFAULT_VERSION_CHOICES.get(default_version)
    default_version = default_version.get('name')

    # Get user input for API key if required
    if requires_gpt:
        api_key = input("Enter your OpenAI API key: ").strip()
    else:
        api_key = ""

    # Get user input for GPT model if required
    default_model = DEFAULT_MODEL
    if requires_gpt:
        print("Choose default GPT model:")
        for key, choice in DEFAULT_MODEL_CHOICES.items():
            print(f"{key}. {choice}")

        default_model = DEFAULT_MODEL_CHOICES.get(input("Enter the number of your choice (default: 1): ").strip() or "1")

    # Get user input for Whisper model size
    print("Choose default Whisper model size:")
    for key, choice in DEFAULT_WHISPER_SIZE_CHOICES.items():
        print(f"{key}. {choice}")

    default_whisper_size = DEFAULT_WHISPER_SIZE_CHOICES.get(input("Enter the number of your choice (default: 1): ").strip() or "1")

    # Save configuration to a JSON file
    config = {
        "API_KEY": api_key,
        "DEFAULT_VERSION": default_version,
        "DEFAULT_MODEL": default_model,
        "DEFAULT_WHISPER_SIZE": default_whisper_size,
        "OBSIDIAN_VAULT_PATH": obsidian_vault_path
    }

    with open("config.json", "w") as config_file:
        json.dump(config, config_file, indent=4)

    print("Configuration saved successfully.")
    install_requirements()
    run_script("run.py")
