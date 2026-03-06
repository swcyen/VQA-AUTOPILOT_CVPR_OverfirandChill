import os
import cv2
import torch
import numpy as np
from PIL import Image
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration

############################################
# CONFIG (do we really need this?)
############################################

VIDEO_DIR = "/workspace/competitions/VQA-AUTOPILOT_CVPR/dataset/videos"
MODEL_NAME = "Qwen/Qwen2-VL-7B-Instruct"

NUM_OUTPUT_FRAMES = 8
GRID_ROWS = 2
GRID_COLS = 4

DEVICE = "cuda"


# Question loader

import json

with open("/workspace/competitions/VQA-AUTOPILOT_CVPR/playground/label_map.json", "r") as f:
    QUESTIONS = json.load(f)

############################################
# VIDEO LOADER
############################################

def load_video_frames(video_path):

    cap = cv2.VideoCapture(video_path)

    frames = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frames.append(frame)

    cap.release()

    return frames


############################################
# FRAME SAMPLER
############################################

def sample_frames(frames, num_output=8):

    total = len(frames)

    if total <= num_output:
        return frames

    candidate_idx = np.linspace(0, total-1, 16).astype(int)

    candidates = [frames[i] for i in candidate_idx]

    scores = []

    for i in range(len(candidates)):
        if i == 0:
            scores.append(0)
            continue

        prev = cv2.cvtColor(candidates[i-1], cv2.COLOR_BGR2GRAY)
        curr = cv2.cvtColor(candidates[i], cv2.COLOR_BGR2GRAY)

        diff = np.mean(cv2.absdiff(prev, curr))
        scores.append(diff)

    scores = np.array(scores)

    top_idx = np.argsort(scores)[-num_output:]

    selected = [candidates[i] for i in sorted(top_idx)]

    return selected


############################################
# GRID BUILDER
############################################

def build_grid(frames, rows=2, cols=4, size=224):

    resized = [cv2.resize(f, (size, size)) for f in frames]

    grid_rows = []

    idx = 0
    for r in range(rows):

        row_imgs = []

        for c in range(cols):

            row_imgs.append(resized[idx])
            idx += 1

        grid_rows.append(np.hstack(row_imgs))

    grid = np.vstack(grid_rows)

    return grid


############################################
# LOAD MODEL
############################################

print("Loading VLM...")

model = Qwen2VLForConditionalGeneration.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto"
)

processor = AutoProcessor.from_pretrained(MODEL_NAME)

print("Model loaded.")


############################################
# VQA FUNCTION
############################################

def ask_vlm(image, question, options):

    img = Image.fromarray(image)

    option_text = "\n".join([f"- {k}" for k in options.keys()])

    prompt = f"""
Answer the question using ONLY one of the options.

Question:
{question}

Options:
{option_text}

Return ONLY the option text exactly.
"""

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": prompt}
            ]
        }
    ]

    text = processor.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = processor(
        text=[text],
        images=[img],
        padding=True,
        return_tensors="pt"
    )

    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

    with torch.inference_mode():
        output = model.generate(
            **inputs,
            max_new_tokens=16,
            synced_gpus=False
        )

    generated_ids = output[:, inputs["input_ids"].shape[-1]:]

    response = processor.batch_decode(
        generated_ids,
        skip_special_tokens=True
    )[0].strip()

    return response


############################################
# MAIN PIPELINE
############################################

def process_video(video_path, question):

    frames = load_video_frames(video_path)

    frames = sample_frames(frames, NUM_OUTPUT_FRAMES)

    grid = build_grid(frames, GRID_ROWS, GRID_COLS)

    answer = ask_vlm(grid, question)

    return answer

## ANSWER MAPPER
def map_answer(text, answer_dict):

    for k, v in answer_dict.items():
        if k.lower() in text.lower():
            return v

    return answer_dict.get("Unknown", -1)

# RUN ALL QUESTIONS
def run_all_questions(video_path):

    frames = load_video_frames(video_path)
    frames = sample_frames(frames, NUM_OUTPUT_FRAMES)
    grid = build_grid(frames)

    results = {}

    for qid, qdata in QUESTIONS.items():

        question = qdata["question"]
        answers = qdata["answers"]

        raw = ask_vlm(grid, question, answers)
        label = map_answer(raw, answers)

        results[qid] = label

    return results

import os
import json

def process_dataset():

    all_results = {}

    videos = sorted(os.listdir(VIDEO_DIR))

    for vid in videos:

        if not vid.endswith(".mp4"):
            continue

        video_path = os.path.join(VIDEO_DIR, vid)

        print("Processing:", vid)

        answers = run_all_questions(video_path)

        video_id = vid.replace(".mp4", "")

        all_results[video_id] = answers

    return all_results
############################################
# RUN
############################################

def main():

    results = process_dataset()

    with open("submission.json", "w") as f:
        json.dump(results, f, indent=2)

    print("Saved submission.json")

if __name__ == "__main__":
    main()
