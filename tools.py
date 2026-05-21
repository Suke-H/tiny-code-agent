import subprocess
from google.genai import types

TOOLS = [types.Tool(function_declarations=[
    types.FunctionDeclaration(
        name="read_file",
        description="ファイルの内容を読む",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={"path": types.Schema(type=types.Type.STRING, description="読むファイルのパス")},
            required=["path"]
        )
    ),
    types.FunctionDeclaration(
        name="write_file",
        description="ファイルを新規作成または上書きする",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "path": types.Schema(type=types.Type.STRING),
                "content": types.Schema(type=types.Type.STRING)
            },
            required=["path", "content"]
        )
    ),
    types.FunctionDeclaration(
        name="append_file",
        description="ファイルの末尾に追記する",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "path": types.Schema(type=types.Type.STRING),
                "content": types.Schema(type=types.Type.STRING)
            },
            required=["path", "content"]
        )
    ),
    types.FunctionDeclaration(
        name="str_replace",
        description="ファイル内の特定の文字列を別の文字列に置き換える。old_strはファイル内に一意に存在する必要がある",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "path": types.Schema(type=types.Type.STRING),
                "old_str": types.Schema(type=types.Type.STRING),
                "new_str": types.Schema(type=types.Type.STRING)
            },
            required=["path", "old_str", "new_str"]
        )
    ),
    types.FunctionDeclaration(
        name="run_command",
        description="シェルコマンドを実行する",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={"command": types.Schema(type=types.Type.STRING)},
            required=["command"]
        )
    ),
])]


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

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
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
    elif name == "run_command":
        return run_command(inputs["command"])
    else:
        return f"error: unknown tool {name}"
