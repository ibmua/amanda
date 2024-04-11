import os
from concurrent.futures import ThreadPoolExecutor
import subprocess

# Get the absolute path of the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Change the current working directory to the script's directory
os.chdir(script_dir)

FILENAME = "outputs/file-filter.prompt"

def process_file(i):
    if os.path.isfile(f"{FILENAME}.{i}"):
        with open(f"outputs/response-of-the-file-filter.{i}", "w") as f:
            f.write(open("response-start-json").read())
        
        subprocess.run([
            "python3", "AI-request.py",
            "--model", "sonnet",
            "--max-tokens", "4096",
            "--temperature", "0.1",
            "--system", "system-request-json",
            "--message-user", f"outputs/file-filter.prompt.{i}",
            "--message-assistant", "response-start-json"
        ], stdout=open(f"outputs/response-of-the-file-filter.{i}", "a"))
        
        # print(i)

def main():
    with ThreadPoolExecutor() as executor:
        futures = []
        i = 0
        while True:
            if os.path.isfile(f"{FILENAME}.{i}"):
                futures.append(executor.submit(process_file, i))
                i += 1
            else:
                break
        
        for future in futures:
            future.result()

if __name__ == "__main__":
    main()