import cv2
import os
import json
import argparse
from datetime import datetime


def extract_frames(video_path, output_dir, frame_interval=30):
    """
    Extrai frames de um vídeo a cada N frames.

    :param video_path: Caminho para o vídeo
    :param output_dir: Pasta onde se criará uma pasta com o resultado da extração
    :param frame_interval: Intervalo de frames (ex: 30 = 1 por segundo se FPS=30)
    """
    video_name = os.path.splitext(os.path.basename(video_path))[0]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    run_folder = f"{video_name}_{timestamp}"

    output_dir = os.path.join(output_dir, run_folder)

    # Criar pasta se não existir
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
            frame_filename = os.path.join(
                output_dir, f"frame_{saved_count:05d}.jpg"
            )
            cv2.imwrite(frame_filename, frame)
            saved_count += 1

        frame_count += 1

    cap.release()

    metadata = {
        "video_path": video_path,
        "fps": fps,
        "total_frames": total_frames,
        "frame_interval": frame_interval,
        "frames_extracted": saved_count
    }

    metadata_path = os.path.join(output_dir, "metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)

    print("Extração concluída.")
    print(f"Frames guardados: {saved_count}")
    print(f"FPS: {fps}")
    print(f"Total frames no vídeo: {total_frames}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Extrair frames de um vídeo com OpenCV"
    )

    parser.add_argument(
        "--video",
        type=str,
        required=True,
        help="Caminho para o vídeo de entrada"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="outputs",
        help="Pasta para guardar os frames"
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Extrair 1 frame a cada N frames"
    )

    args = parser.parse_args()

    extract_frames(
        video_path=args.video,
        output_dir=args.output,
        frame_interval=args.interval
    )