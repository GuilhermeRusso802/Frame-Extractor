import argparse
import logging

from extractor import extract_frames


def main():
    """
    Interface de linha de comandos para extração de frames de vídeo.

    Permite executar o pipeline de extração sem interface gráfica,
    usando parâmetros diretamente do terminal.

    Funcionalidades:
        - Definir vídeo de entrada.
        - Definir pasta de output.
        - Definir intervalo de frames.
        - Definir intervalo temporal (start/end em segundos).
        - Definir formato e qualidade da imagem.

    Exemplo de uso:
        python main.py --video video.mp4 --output outputs --interval 30
        python main.py --video video.mp4 --output outputs \
            --interval 15 --start-time 10 --end-time 60 \
            --image-format jpg --jpeg-quality 95
    """
    parser = argparse.ArgumentParser(
        description="Extrair frames de vídeo"
    )

    parser.add_argument(
        "--video",
        type=str,
        required=True,
        help="Caminho do vídeo",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="outputs",
        help="Pasta de saída",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Extrair 1 frame a cada N",
    )
    parser.add_argument(
        "--start-time",
        type=float,
        default=0,
        help="Tempo inicial em segundos (default: 0)",
    )
    parser.add_argument(
        "--end-time",
        type=float,
        default=None,
        help="Tempo final em segundos (default: fim do vídeo)",
    )
    parser.add_argument(
        "--image-format",
        type=str,
        default="jpg",
        choices=["jpg", "png"],
        help="Formato das imagens extraídas (default: jpg)",
    )
    parser.add_argument(
        "--jpeg-quality",
        type=int,
        default=95,
        help="Qualidade JPEG entre 1 e 100 (default: 95)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Mostrar logs detalhados",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    result = extract_frames(
        video_path=args.video,
        output_dir=args.output,
        frame_interval=args.interval,
        start_time=args.start_time,
        end_time=args.end_time,
        image_format=args.image_format,
        jpeg_quality=args.jpeg_quality,
    )

    print("Extração concluída.")
    print(result)


if __name__ == "__main__":
    main()