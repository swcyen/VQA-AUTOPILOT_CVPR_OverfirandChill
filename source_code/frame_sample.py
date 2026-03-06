import cv2
import os

def sample_frames(video_path, out_dir, n_frames=8):

    os.makedirs(out_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    indices = [int(total * p) for p in [0.1,0.2,0.4,0.6,0.75,0.85,0.93,0.97]]

    frames = []

    for i, idx in enumerate(indices):

        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()

        if not ret:
            continue

        frame = cv2.resize(frame,(384,384))

        path = os.path.join(out_dir,f"frame_{i}.jpg")

        cv2.imwrite(path, frame)

        frames.append(path)

    cap.release()

    return frames
