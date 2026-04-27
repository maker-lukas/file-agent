## File Agent

![file_agent](https://cdn.hackclub.com/019dd019-5fa2-7842-a988-0e93b7bcc96a/file_agent.png)


An ai file organizer that can create and move files around!

I made this project to play around with ai agents and instructions.txt which I think are pretty interesting and I just wanted to try it out.

## VIDEO DEMO

**Click on the button to watch the DEMO its not a broken link PyPI does not support video previews! ∨∨∨∨**

also sorry if i'm a bit stutery i do that sometimes :(

https://cdn.hackclub.com/019dd072-94c3-7175-b43d-b1520c7d277b/file_agent_demo.mp4

### Install

```bash
pip install file-agent
```

### Config

1. Go to https://ai.hackclub.com
2. Go to the Models tab and pick a model (Qwen3 32B works well)
3. Go to the Keys tab and create a new API key
4. Copy the key
5. Create `~/.file-agent.env` (see .env.example):
```
OPENAI_API_KEY=your-key-here          # get from ai.hackclub.com Keys tab
OPENAI_BASE_URL=https://ai.hackclub.com/proxy/v1
MODEL=qwen/qwen3-32b                  # model from the Models tab
```

### Usage

run:

```bash
file-agent
```

Drop files into `~/file-agent/sandbox` and watch them get organized. Press `Ctrl+C` to stop.

### Features

- Automatically organizes files by type (images, code, audio, etc)
- Creates folders if needed
- Watches for new files with watchdog
- Activity logs

### Safety

The ai can only access files in the sandbox folder. If it even tries to leave, the program stops with an error :3

### How it works

1. Python tools scan the sandbox and list all files with their extensions
2. The file list gets sent to an ai model
3. The ai decides how to organize everything and responds with JSON
4. Python tools read that JSON and:
   - Create any needed folders
   - Move files into the right places
5. The system keeps watching for more files

### Logs

logs are saved at `~/file-agent/log.txt`.

---