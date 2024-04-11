import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess

# Get the absolute path of the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Change the current working directory to the script's directory
os.chdir(script_dir)

FILENAME = "outputs/file-filter.prompt"
MAX_INSTANCES = 5

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

def main():
    amanda_api = os.getenv("AMANDA_API")
    if amanda_api == "google":
        i = 0
        while True:
            with ThreadPoolExecutor(max_workers=MAX_INSTANCES) as executor:
                futures = []
                for _ in range(MAX_INSTANCES):
                    if os.path.isfile(f"{FILENAME}.{i}"):
                        futures.append(executor.submit(process_file, i))
                        i += 1
                    else:
                        break
                if not futures:
                    break
                for future in as_completed(futures):
                    future.result()
    else:
        i = 0
        while True:
            if os.path.isfile(f"{FILENAME}.{i}"):
                process_file(i)
                i += 1
            else:
                break

if __name__ == "__main__":
    main()