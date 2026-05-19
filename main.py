import os
from agent import agent_loop, compact


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("エラー: ANTHROPIC_API_KEY が設定されていません。")
        return

    print("コードエージェント起動。/compact で履歴を圧縮、/exit で終了。")
    messages = []

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n終了します。")
            break

        if not user_input:
            continue

        if user_input == "/exit":
            print("終了します。")
            break

        if user_input == "/compact":
            messages = compact(messages)
            continue

        messages.append({"role": "user", "content": user_input})
        messages = agent_loop(messages)


if __name__ == "__main__":
    main()
