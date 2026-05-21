import csv, json, re
from google.genai import types


def _part_to_str(role, part):
    if part.text:
        return role, part.text
    elif part.function_call:
        args = json.dumps(dict(part.function_call.args), ensure_ascii=False)
        return role, f"<function_call> {part.function_call.name}({args})"
    elif part.function_response:
        return f"{role}(tool_result:{part.function_response.name})", str(part.function_response.response)
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
        role = row["role"]
        content = row["content"]
        api_role = "user" if role.startswith("user") else "model"

        if role.startswith("user(tool_result:"):
            fn_name = role[len("user(tool_result:"):-1]
            messages.append(types.Content(role="user", parts=[types.Part(
                function_response=types.FunctionResponse(name=fn_name, response={"result": content})
            )]))
        elif content.startswith("<function_call>"):
            m = re.match(r"<function_call> (\w+)\((.+)\)$", content, re.DOTALL)
            name, args = m.group(1), json.loads(m.group(2))
            messages.append(types.Content(role="model", parts=[types.Part(
                function_call=types.FunctionCall(name=name, args=args)
            )]))
        else:
            messages.append(types.Content(role=api_role, parts=[types.Part(text=content)]))

    return messages
