import csv
import os
from datetime import datetime
from agent import agent_loop, compact
from logger import load_from_csv
from google.genai import types


def main():
    if not os.environ.get("GEMINI_API_KEY"):
        print("エラー: GEMINI_API_KEY が設定されていません。")
        return

    os.makedirs("logs", exist_ok=True)
    log_path = datetime.now().strftime("logs/%Y%m%d_%H%M%S.csv")
    log_file = open(log_path, "w", encoding="utf-8", newline="")
    call_counter = [0]

    writer = csv.writer(log_file)
    writer.writerow(["call_num", "type", "role", "content"])
    writer.writerow(["", "session_start", "", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    log_file.flush()

    print("コードエージェント起動。/compact で履歴を圧縮、/resume [path] で再開、/exit で終了。")
    messages = []

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n終了します。")
            csv.writer(log_file).writerow(["", "session_end", "", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            log_file.close()
            break

        if not user_input:
            continue

        if user_input == "/exit":
            print("終了します。")
            csv.writer(log_file).writerow(["", "session_end", "", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            log_file.close()
            break

        if user_input.startswith("/resume"):
            parts = user_input.split(maxsplit=1)
            if len(parts) == 2:
                csv_path = parts[1]
            else:
                log_files = sorted(os.listdir("logs"))
                for i, f in enumerate(log_files):
                    print(f"  [{i}] {f}")
                idx = input("番号を選択: ").strip()
                csv_path = os.path.join("logs", log_files[int(idx)])
            messages = load_from_csv(csv_path)
            if not messages:
                print(f"[resume] {csv_path} に復元できる履歴がありません")
                continue
            print(f"[resume] {csv_path} から再開")
            continue

        if user_input == "/compact":
            messages = compact(messages, log_file, call_counter)
            continue

        messages.append(types.Content(role="user", parts=[types.Part(text=user_input)]))
        messages = agent_loop(messages, log_file, call_counter)


if __name__ == "__main__":
    main()
