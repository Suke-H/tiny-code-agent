import json
import os
import google.genai as genai
from google.genai import types
from tools import execute_tool
from logger import _part_to_str, write_call

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

MODEL = "gemini-2.5-flash"
SYSTEM = """あなたはコードエージェントです。以下のツールが使えます：
- read_file(path): ファイルを読む
- write_file(path, content): ファイルを一括作成（上書き）
- append_file(path, content): ファイルに追記
- str_replace(path, old_str, new_str): ファイル内の文字列を置換（old_strはファイル内に一意に存在する必要がある）
- run_code(code): Pythonコードを実行

タスクが完了したら type=terminate で result に最終回答を入れてください。"""


AGENT_ACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "type":   {"type": "string", "enum": ["tool_call", "terminate"]},
        "name":   {"type": "string"},
        "args":   {"type": "object", "additionalProperties": {}},
        "result": {"type": "string"},
    },
    "required": ["type"],
}


def _messages_to_text(messages):
    lines = []
    for m in messages:
        for part in m.parts:
            if part.text:
                lines.append(f"[{m.role}]: {part.text}")
    return "\n".join(lines)


def compact(messages, log_file=None, call_counter=None):
    if not messages:
        return messages

    history_text = _messages_to_text(messages)
    compact_input = [types.Content(role="user", parts=[types.Part(text=(
        f"以下の会話履歴を要約してください。重要な決定、ファイルの状態、未完了タスクを含めてください。\n\n{history_text}"
    ))])]
    response = client.models.generate_content(
        model=MODEL,
        contents=compact_input,
    )
    summary = response.text
    write_call(log_file, call_counter, compact_input, [("model", summary)])
    print(f"\n[compact] 履歴を要約しました（{len(messages)}メッセージ → 1メッセージ）\n")

    return [
        types.Content(role="user", parts=[types.Part(text=f"【これまでの作業要約】\n{summary}")]),
        types.Content(role="model", parts=[types.Part(text="わかりました。続けます。")])
    ]


def agent_loop(messages, log_file=None, call_counter=None):
    while True:
        response = client.models.generate_content(
            model=MODEL,
            contents=messages,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM,
                response_json_schema=AGENT_ACTION_SCHEMA,
                response_mime_type="application/json",
            )
        )

        action = json.loads(response.text)
        model_content = types.Content(role="model", parts=[types.Part(text=response.text)])

        write_call(log_file, call_counter, messages, [("model", response.text)])
        messages.append(model_content)

        if action["type"] == "terminate":
            print(f"\nAssistant: {action['result']}")
            break

        args = action.get("args") or {}
        print(f"[tool] {action['name']}({json.dumps(args, ensure_ascii=False)})")
        result = execute_tool(action["name"], args)
        messages.append(types.Content(role="user", parts=[types.Part(
            text=f"[tool_result] {action['name']}: {result}"
        )]))

    return messages
