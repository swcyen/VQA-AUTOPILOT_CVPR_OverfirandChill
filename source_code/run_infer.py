import os
import cv2
import torch
import numpy as np
from PIL import Image
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration

############################################
# CONFIG
############################################

VIDEO_DIR = "videos"
MODEL_NAME = "Qwen/Qwen2-VL-7B-Instruct"

NUM_OUTPUT_FRAMES = 8
GRID_ROWS = 2
GRID_COLS = 4

DEVICE = "cuda"


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

def ask_vlm(image, question):

    img = Image.fromarray(image)

    prompt = f"""
You are analyzing frames from a driving video.

Question: {question}

Answer with ONE WORD.
"""

    inputs = processor(
        text=prompt,
        images=img,
        return_tensors="pt"
    ).to(DEVICE)

    output = model.generate(
        **inputs,
        max_new_tokens=8
    )

    text = processor.batch_decode(
        output,
        skip_special_tokens=True
    )[0]

    return text.strip()


############################################
# MAIN PIPELINE
############################################

def process_video(video_path, question):

    frames = load_video_frames(video_path)

    frames = sample_frames(frames, NUM_OUTPUT_FRAMES)

    grid = build_grid(frames, GRID_ROWS, GRID_COLS)

    answer = ask_vlm(grid, question)

    return answer


############################################
# RUN
############################################

def main():

    question = "What color is the traffic light?"

    for video in os.listdir(VIDEO_DIR):

        path = os.path.join(VIDEO_DIR, video)

        print("Processing:", video)

        ans = process_video(path, question)

        print("Answer:", ans)
        print()


if __name__ == "__main__":
    main()
