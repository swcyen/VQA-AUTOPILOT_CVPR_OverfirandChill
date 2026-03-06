import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import argparse

# ===== nhận input từ terminal =====
parser = argparse.ArgumentParser()

parser.add_argument(
    "--video_dir",
    type=str,
    required=True,
    help="Đường dẫn đến thư mục video"
)

parser.add_argument(
    "--save_path",
    type=str,
    required=True,
    help="Đường dẫn lưu ảnh biểu đồ"
)

args = parser.parse_args()

video_dir = args.video_dir
save_path = args.save_path

durations = []

# ===== đọc video =====
for video in os.listdir(video_dir):

    if not video.endswith(".mp4"):
        continue

    path = os.path.join(video_dir, video)

    cap = cv2.VideoCapture(path)

    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    duration = frames / fps if fps > 0 else 0
    durations.append(duration)

    cap.release()

durations = np.array(durations)

# ===== thống kê =====
total_videos = len(durations)
avg_duration = durations.mean()

rounded = np.round(durations, 1)
most_common_duration, count = Counter(rounded).most_common(1)[0]

total_duration = durations.sum()
total_minutes = total_duration / 60
total_hours = total_duration / 3600

print("===== THỐNG KÊ DATASET =====")
print("Tổng số video:", total_videos)
print("Độ dài trung bình:", round(avg_duration, 2), "giây")
print("Độ dài phổ biến nhất:", most_common_duration, "giây (", count, "video )")
print("Tổng thời lượng:", round(total_duration, 2), "giây")
print("Tổng thời lượng:", round(total_minutes, 2), "phút")
print("Tổng thời lượng:", round(total_hours, 2), "giờ")

# ===== vẽ biểu đồ =====
plt.figure(figsize=(8,5))

plt.hist(durations, bins=30)

plt.axvline(avg_duration, linestyle='dashed',
            label=f"Trung bình = {avg_duration:.2f}s")

plt.axvline(most_common_duration, linestyle='dotted',
            label=f"Phổ biến nhất ≈ {most_common_duration}s")

plt.xlabel("Độ dài video (giây)")
plt.ylabel("Số lượng video")
plt.title("Phân bố độ dài video")

plt.legend()

# ===== ghi thông tin lên hình =====
plt.text(
    0.98, 0.95,
    f"Tổng số video: {total_videos}\n"
    f"Tổng thời lượng: {total_minutes:.2f} phút\n"
    f"({total_hours:.2f} giờ)",
    transform=plt.gca().transAxes,
    ha="right",
    va="top",
    bbox=dict(facecolor="white", alpha=0.8)
)

plt.grid(alpha=0.3)

# ===== lưu ảnh =====
plt.savefig(save_path, dpi=300)
plt.close()

print("Đã lưu biểu đồ tại:", save_path)