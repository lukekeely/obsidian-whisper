import os
import json
import subprocess

# Function to check if the configuration JSON exists
def config_exists():
    return os.path.exists("config.json")

# Function to run the selected script
def run_script(script_name):
    try:
        subprocess.run(["python", script_name], check=True)
    except subprocess.CalledProcessError:
        print(f"Failed to run the script: {script_name}")

# Main run script
if __name__ == "__main__":
    if not config_exists():
        print("Configuration not found. Running setup script...")
        subprocess.run(["python", "setup.py"], check=True)
    
    # Read the configuration from the JSON file
    with open("config.json", "r") as config_file:
        config = json.load(config_file)

    # Determine which script to run based on the selected default version
    default_version = config.get("DEFAULT_VERSION", "2")
    print(f'Running {default_version}.py')
    run_script(f'{default_version}.py')