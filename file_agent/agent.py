import json
import time
import os
import threading
from datetime import datetime
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from openai import OpenAI

load_dotenv(os.path.expanduser("~/file-agent/.env"))

APP_DIR = os.path.expanduser("~/file-agent")
SANDBOX_DIR = os.path.join(APP_DIR, "sandbox")
LOG_FILE = os.path.join(APP_DIR, "log.txt")
ENV_FILE = os.path.join(APP_DIR, ".env")

os.makedirs(APP_DIR, exist_ok=True)
os.makedirs(SANDBOX_DIR, exist_ok=True)

if not os.path.exists(ENV_FILE):
    with open(ENV_FILE, "w") as f:
        f.write("""OPENAI_API_KEY=your-api-key-here          # get from ai.hackclub.com Keys tab
OPENAI_BASE_URL=https://ai.hackclub.com/proxy/v1
MODEL=qwen/qwen3-32b                  # model from the Models tab
""")
    print(f"{Yellow}Created config at {ENV_FILE}{Reset}")
    print(f"{Yellow}Add your API key and run again!{Reset}")
    exit(0)

def log_to_file(msg):
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

Cyan = "\033[96m"
Green = "\033[92m"
Yellow = "\033[93m"
Red = "\033[91m"
Blue = "\033[94m"
Reset = "\033[0m"

DEFAULT_BASE_URL = "https://ai.hackclub.com/proxy/v1"
DEFAULT_MODEL = "qwen/qwen3-32b"

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print(f"{Red}Error:{Reset} OPENAI_API_KEY not set. Create ~/.file-agent.env with your API key.")
    print(f"Get one at: https://ai.hackclub.com")
    exit(1)

client = OpenAI(
    api_key=api_key,
    base_url=os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE_URL),
    http_client=None
)

from importlib.resources import files as pkg_files

from file_agent.tools import list_dir, create_file, create_folder, delete, move
from file_agent.sandbox import SANDBOX_DIR
os.makedirs(SANDBOX_DIR, exist_ok=True)

system_prompt = pkg_files("file_agent").joinpath("instructions.txt").read_text()

def scan_sandbox():
    entries = os.listdir(SANDBOX_DIR)
    if not entries:
        return None
    labeled = []
    for e in entries:
        full = os.path.join(SANDBOX_DIR, e)
        if os.path.isdir(full):
            labeled.append(f"[folder] {e}")
        else:
            labeled.append(f"[file] {e}")
    return ", ".join(labeled)

def run_actions(actions):
    for action in actions:
        name = action.get("action")
        try:
            if name == "create_folder":
                msg = create_folder(action['path'])
                print(f"  {Green}->{Reset} {msg}")
                log_to_file(msg)
            elif name == "move":
                msg = move(action['src'], action['dst'])
                print(f"  {Green}->{Reset} {msg}")
                log_to_file(msg)
            elif name == "delete":
                msg = delete(action['path'])
                print(f"  {Green}->{Reset} {msg}")
                log_to_file(msg)
            elif name == "create_file":
                msg = create_file(action['path'], action.get('content', ''))
                print(f"  {Green}->{Reset} {msg}")
                log_to_file(msg)
            else:
                msg = f"Unknown action: {name}"
                print(f"  {Red}->{Reset} {msg}")
                log_to_file(msg)
        except Exception as e:
            msg = f"Error: {e}"
            print(f"  {Red}->{Reset} {msg}")
            log_to_file(msg)

class SandboxHandler(FileSystemEventHandler):
    def __init__(self):
        self.timer = None
    
    def on_created(self, event):
        if event.is_directory:
            return

        parent = os.path.dirname(event.src_path)
        if os.path.realpath(parent) != SANDBOX_DIR:
            return
        msg = f"New file: {os.path.basename(event.src_path)}"
        print(f"\n{Yellow}->{Reset} {msg}")
        log_to_file(msg)
        self.schedule_organize()

    def schedule_organize(self):
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(3.0, organize)
        self.timer.start()

def organize():
    snapshot = scan_sandbox()
    if not snapshot:
        return

    loose_files = [e for e in snapshot.split(", ") if e.startswith("[file]")]
    if loose_files:
        msg = f"Organizing: {', '.join(loose_files)}"
        print(f"\n{Cyan}{msg}{Reset}")
        log_to_file(msg)
    else:
        return

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Here are the files and folders in the sandbox:\n{snapshot}"}
    ]

    try:
        response = client.chat.completions.create(
            model=os.environ.get("MODEL", DEFAULT_MODEL),
            messages=messages
        )
    except Exception as e:
        print(f"{Red}API error:{Reset} {e}")
        return

    reply = response.choices[0].message.content

    reply = reply.strip()
    if reply.startswith("```"):
        reply = reply.split("\n", 1)[1]
        reply = reply.rsplit("```", 1)[0]

    try:
        actions = json.loads(reply)
    except json.JSONDecodeError:
        print(f"{Red}Bad response:{Reset} {reply[:100]}")
        return

    if not actions:
        print(f"{Yellow}Nothing to organize{Reset}")
        return

    print(f"\n{Blue}Performing {len(actions)} actions:{Reset}")
    run_actions(actions)
    print(f"{Green}Watching for changes...{Reset}\n")

def main():
    print(f"\n{Green}File agent started{Reset}")
    print(f"Watching: {Blue}{SANDBOX_DIR}{Reset}")
    print(f"{Yellow}Press Ctrl+C to stop{Reset}\n")
    log_to_file("File agent started")

    organize()

    print(f"\n{Green}Watching for changes...{Reset}\n")
    log_to_file("Watching for changes...")

    handler = SandboxHandler()
    observer = Observer()
    observer.schedule(handler, SANDBOX_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Red}Stopped{Reset}")
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()