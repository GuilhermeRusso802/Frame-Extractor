import cv2
import os
import json
import time
from datetime import datetime


def extract_frames(video_path, output_dir="outputs", frame_interval=30):
    """
    Extrai frames de um vídeo a cada N frames.
    """

    if frame_interval <= 0:
        raise ValueError("O intervalo deve ser maior que zero.")

    start_time = time.time()

    video_name = os.path.splitext(os.path.basename(video_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    run_folder = f"{video_name}_{timestamp}"
    output_dir = os.path.join(output_dir, run_folder)

    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError("Erro ao abrir o vídeo.")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frame_count = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        if frame_count % frame_interval == 0:
            filename = os.path.join(
                output_dir,
                f"frame_{saved_count:05d}.jpg"
            )

            cv2.imwrite(filename, frame)
            saved_count += 1

        frame_count += 1

    cap.release()

    elapsed = round(time.time() - start_time, 2)

    metadata = {
        "video_name": video_name,
        "video_path": video_path,
        "output_directory": output_dir,
        "processing_date": timestamp,
        "fps": fps,
        "total_frames": total_frames,
        "frame_interval": frame_interval,
        "frames_extracted": saved_count,
        "processing_time_seconds": elapsed
    }

    metadata_path = os.path.join(output_dir, "metadata.json")

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)

    return metadata