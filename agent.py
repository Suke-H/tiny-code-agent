import json
import anthropic
from tools import TOOLS, execute_tool

client = anthropic.Anthropic()


def compact(messages):
    if not messages:
        return messages

    history_text = json.dumps(messages, ensure_ascii=False, indent=2)
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": f"以下の会話履歴を要約してください。重要な決定、ファイルの状態、未完了タスクを含めてください。\n\n{history_text}"
            }
        ]
    )
    summary = response.content[0].text
    print(f"\n[compact] 履歴を要約しました（{len(messages)}メッセージ → 1メッセージ）\n")

    return [
        {"role": "user", "content": f"【これまでの作業要約】\n{summary}"},
        {"role": "assistant", "content": "わかりました。続けます。"}
    ]


def agent_loop(messages):
    while True:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=4096,
            system="あなたはコードエージェントです。ファイル操作やコマンド実行を通じてタスクを完了してください。",
            tools=TOOLS,
            messages=messages
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    print(f"\nAssistant: {block.text}")
            break

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"[tool] {block.name}({json.dumps(block.input, ensure_ascii=False)})")
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        messages.append({"role": "user", "content": tool_results})

    return messages
