import re
import json

input_file = "legend.txt"
output_file = "label_map.json"

data = {}
current_q = None

with open(input_file, "r", encoding="utf-8") as f:
    lines = [l.strip() for l in f.readlines()]

for line in lines:

    q_match = re.match(r"(Q\d+\.[a-z]|Q\d+):\s*(.*)", line)

    if q_match:
        qid = q_match.group(1)
        question_text = q_match.group(2)

        current_q = qid
        data[current_q] = {
            "question": question_text,
            "answers": {}
        }
        continue

    ans_match = re.match(r"(.+?)\s*=\s*(-?\d+)", line)

    if ans_match and current_q:
        answer = ans_match.group(1).strip()
        value = int(ans_match.group(2))

        data[current_q]["answers"][answer] = value

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Saved:", output_file)