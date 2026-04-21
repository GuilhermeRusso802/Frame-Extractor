import argparse
from extractor import extract_frames


def main():
    parser = argparse.ArgumentParser(
        description="Extrair frames de vídeo"
    )

    parser.add_argument(
        "--video",
        type=str,
        required=True,
        help="Caminho do vídeo"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="outputs",
        help="Pasta de saída"
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Extrair 1 frame a cada N"
    )

    args = parser.parse_args()

    result = extract_frames(
        video_path=args.video,
        output_dir=args.output,
        frame_interval=args.interval
    )

    print("Extração concluída.")
    print(result)


if __name__ == "__main__":
    main()