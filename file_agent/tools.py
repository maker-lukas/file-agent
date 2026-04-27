import os
import shutil

from file_agent.sandbox import safe_path



def list_dir(path="."):
    resolved = safe_path(path)
    return os.listdir(resolved)

def create_file(path, content=""):
    resolved = safe_path(path)
    os.makedirs(os.path.dirname(resolved), exist_ok=True)
    with open(resolved, "w") as f:
        f.write(content)
    return f"Created file: {path}"

def create_folder(path):
    resolved = safe_path(path)
    os.makedirs(resolved, exist_ok=True)
    return f"Created folder: {path}"

def delete(path):
    resolved = safe_path(path)
    if os.path.isfile(resolved):
        os.remove(resolved)
    elif os.path.isdir(resolved):
        shutil.rmtree(resolved)
    else:
        return f"Not found: {path}"
    return f"Deleted: {path}"

def move(src, dst):
    resolved_src = safe_path(src)
    resolved_dst = safe_path(dst)
    os.makedirs(os.path.dirname(resolved_dst), exist_ok=True)
    shutil.move(resolved_src, resolved_dst)
    return f"Moved: {src} -> {dst}"


if __name__ == "__main__":
    print(create_file("test.txt", "hello world"))
    print(list_dir())
    print(delete("test.txt"))
    print(list_dir())