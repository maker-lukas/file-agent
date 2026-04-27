import os
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/file-agent/.env"))

SANDBOX_DIR = os.path.realpath(os.path.expanduser("~/file-agent/sandbox"))

def safe_path(path):
    resolved = os.path.realpath(os.path.join(SANDBOX_DIR, path))

    if not resolved.startswith(SANDBOX_DIR):
        raise ValueError(f"Path '{path}' escapes the sandbox!")

    return resolved

if __name__ == "__main__":
    print(safe_path("test.txt"))
    print(safe_path("../../etc/passwd"))