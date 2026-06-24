import csv, json
from google.genai import types


def _part_to_str(role, part):
    if part.text:
        return role, part.text
    return None


def write_call(log_file, call_counter, messages, response_parts):
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


def load_from_csv(csv_path):
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["call_num"].isdigit():
                rows.append(row)

    if not rows:
        return []
    last_num = str(max(int(r["call_num"]) for r in rows))
    input_rows = [r for r in rows if r["call_num"] == last_num and r["type"] == "input"]

    messages = []
    for row in input_rows:
        api_role = "user" if row["role"] == "user" else "model"
        messages.append(types.Content(role=api_role, parts=[types.Part(text=row["content"])]))

    return messages
