import subprocess

def read_file(path):
    with open(path, "r") as f:
        return f.read()

def write_file(path, content):
    with open(path, "w") as f:
        f.write(content)
    return "success"

def append_file(path, content):
    with open(path, "a") as f:
        f.write(content)
    return "success"

def str_replace(path, old_str, new_str):
    with open(path, "r") as f:
        text = f.read()
    if old_str not in text:
        return f"error: old_str not found in {path}"
    if text.count(old_str) > 1:
        return f"error: old_str is not unique in {path}"
    text = text.replace(old_str, new_str, 1)
    with open(path, "w") as f:
        f.write(text)
    return "success"

def run_code(code):
    result = subprocess.run(["uv", "run", "python", "-c", code], capture_output=True, text=True)
    return result.stdout + result.stderr


def execute_tool(name, inputs):
    if name == "read_file":
        return read_file(inputs["path"])
    elif name == "write_file":
        return write_file(inputs["path"], inputs["content"])
    elif name == "append_file":
        return append_file(inputs["path"], inputs["content"])
    elif name == "str_replace":
        return str_replace(inputs["path"], inputs["old_str"], inputs["new_str"])
    elif name == "run_code":
        return run_code(inputs["code"])
    else:
        return f"error: unknown tool {name}"
