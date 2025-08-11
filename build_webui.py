import os
import shutil
import subprocess
import sys


def run_command(command, cwd):
    """Runs a command in a specified directory and checks for errors."""
    print(f"Executing: {' '.join(command)} in {cwd}")
    try:
        process = subprocess.Popen(command, cwd=cwd, shell=True, stdout=sys.stdout, stderr=sys.stderr)
        process.communicate()
        if process.returncode != 0:
            print(f"Error: Command '{' '.join(command)}' failed with exit code {process.returncode}")
            sys.exit(process.returncode)
    except Exception as e:
        print(f"An exception occurred while running command: {' '.join(command)}")
        print(e)
        sys.exit(1)

def main():
    """Main function to build and deploy the WebUI."""
    print("########## WebUI Build Script (Python) ##########")
    
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define paths
    webui_dir = os.path.join(script_dir, "webui", "bilichat-webui")
    output_dir = os.path.join(webui_dir, "out")
    target_dir = os.path.join(script_dir, "nonebot_plugin_bilichat", "static", "html")
    
    # 1. Install dependencies
    print("\n[1/3] Installing dependencies with bun...")
    run_command(["bun", "install"], cwd=webui_dir)
    
    # 2. Build the project
    print("\n[2/3] Building the WebUI project...")
    run_command(["bun", "run", "build"], cwd=webui_dir)
    
    # 3. Deploy to target directory
    print("\n[3/3] Deploying to target directory...")
    if os.path.exists(target_dir):
        print(f"Deleting old files from {target_dir}...")
        shutil.rmtree(target_dir)
    
    print(f"Copying new files from {output_dir} to {target_dir}...")
    shutil.copytree(output_dir, target_dir)
    
    print("\n########## Build and Deploy Succeeded ##########\n")

if __name__ == "__main__":
    main()
