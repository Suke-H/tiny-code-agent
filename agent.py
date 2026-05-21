import csv
import json
import os
import google.genai as genai
from google.genai import types
from tools import TOOLS, execute_tool


def _part_to_str(role, part):
    if part.text:
        return role, part.text
    elif part.function_call:
        args = json.dumps(dict(part.function_call.args), ensure_ascii=False)
        return role, f"<function_call> {part.function_call.name}({args})"
    elif part.function_response:
        return f"{role}(tool_result)", str(part.function_response.response)
    return None


def _write_call(log_file, call_counter, messages, response_parts):
    if log_file is None:
        return
    call_counter[0] += 1
    n = call_counter[0]
    writer = csv.writer(log_file)
    for m in messages:
        for part in m.parts:
            row = _part_to_str(m.role, part)
            if row:
                writer.writerow([n, "input", row[0], row[1]])
    for role, content in response_parts:
        writer.writerow([n, "output", role, content])
    log_file.flush()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

MODEL = "gemini-2.5-flash"
SYSTEM = "あなたはコードエージェントです。ファイル操作やコマンド実行を通じてタスクを完了してください。"


def _messages_to_text(messages):
    lines = []
    for m in messages:
        for part in m.parts:
            if part.text:
                lines.append(f"[{m.role}]: {part.text}")
            elif part.function_call:
                lines.append(f"[tool_call]: {part.function_call.name}({dict(part.function_call.args)})")
            elif part.function_response:
                lines.append(f"[tool_result]: {part.function_response.response}")
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
    _write_call(log_file, call_counter, compact_input, [("model", summary)])
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
                tools=TOOLS,
            )
        )

        candidate = response.candidates[0]

        output_parts = []
        for part in candidate.content.parts:
            row = _part_to_str("model", part)
            if row:
                output_parts.append(row)
        _write_call(log_file, call_counter, messages, output_parts)

        messages.append(candidate.content)

        has_function_call = any(p.function_call for p in candidate.content.parts)

        if not has_function_call:
            print(f"\nAssistant: {response.text}")
            break

        function_responses = []
        for part in candidate.content.parts:
            if part.function_call:
                fc = part.function_call
                args = dict(fc.args)
                print(f"[tool] {fc.name}({json.dumps(args, ensure_ascii=False)})")
                result = execute_tool(fc.name, args)
                function_responses.append(types.Part(
                    function_response=types.FunctionResponse(
                        name=fc.name,
                        response={"result": result}
                    )
                ))

        messages.append(types.Content(role="user", parts=function_responses))

    return messages
