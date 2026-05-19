import cv2
import os
import json
import time
import logging
from datetime import datetime
from typing import Callable, Optional

logger = logging.getLogger(__name__)


def safe_imwrite(path: str, frame, jpeg_quality: int = 95) -> bool:
    """
    Guarda um frame de vídeo no disco de forma segura.

    Usa cv2.imencode + escrita manual em vez de cv2.imwrite direto, para
    suportar caminhos com caracteres não-ASCII (acentos, cedilhas), que
    são comuns em sistemas Windows configurados em português.

    Args:
        path (str): caminho completo do ficheiro de saída.
        frame (numpy.ndarray): frame do vídeo em formato OpenCV (BGR).
        jpeg_quality (int): qualidade JPEG (1-100). Apenas usado quando
            a extensão é .jpg/.jpeg.

    Returns:
        bool: True se o ficheiro foi guardado com sucesso, False caso contrário.
    """
    try:
        ext = os.path.splitext(path)[1].lower()

        params = []
        if ext in (".jpg", ".jpeg"):
            params = [cv2.IMWRITE_JPEG_QUALITY, int(jpeg_quality)]

        success, buffer = cv2.imencode(ext, frame, params)

        if not success:
            return False

        with open(path, "wb") as f:
            f.write(buffer.tobytes())

        return True

    except Exception as e:
        logger.exception("Erro ao escrever frame em %s: %s", path, e)
        return False


def extract_frames(
    video_path: str,
    output_dir: str,
    frame_interval: int = 30,
    start_time: float = 0,
    end_time: Optional[float] = None,
    image_format: str = "jpg",
    jpeg_quality: int = 95,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> dict:
    """
    Extrai frames de um vídeo dentro de um intervalo temporal definido.

    O processo:
        - valida parâmetros de entrada;
        - abre o vídeo com OpenCV;
        - calcula FPS e duração;
        - converte tempos (segundos -> frames);
        - salta rapidamente até ao frame inicial usando cap.grab();
        - percorre o vídeo frame a frame até end_time;
        - guarda frames de acordo com o intervalo definido;
        - gera metadata com informação do processamento.

    Args:
        video_path (str): caminho do vídeo de entrada.
        output_dir (str): diretório base onde serão guardados os resultados.
        frame_interval (int): intervalo de frames entre extrações (deve ser > 0).
        start_time (float): tempo inicial em segundos.
        end_time (float | None): tempo final em segundos (ou None para fim do vídeo).
        image_format (str): formato de imagem ("jpg" ou "png").
        jpeg_quality (int): qualidade JPEG (1-100).
        progress_callback (callable | None): função opcional chamada
            periodicamente com (frame_atual, frame_final) para reportar progresso.

    Returns:
        dict: metadata do processamento contendo:
            - video_name
            - output_dir
            - start_time / end_time
            - fps
            - duration
            - frames_extracted
            - processing_time

    Raises:
        FileNotFoundError: se o vídeo não existir.
        ValueError: se parâmetros forem inválidos ou o vídeo não abrir.
    """
    # --- Validações de entrada ---
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Vídeo não encontrado: {video_path}")

    if frame_interval <= 0:
        raise ValueError("O intervalo deve ser maior que zero.")

    if start_time < 0:
        raise ValueError("start_time não pode ser negativo.")

    if image_format.lower() not in ("jpg", "jpeg", "png"):
        raise ValueError("image_format deve ser 'jpg' ou 'png'.")

    start_process = time.time()

    video_name = os.path.splitext(os.path.basename(video_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_folder = f"{video_name}_{timestamp}"

    output_dir = os.path.abspath(output_dir)
    output_dir = os.path.normpath(os.path.join(output_dir, run_folder))
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Erro ao abrir vídeo: {video_path}")

    try:
        fps = cap.get(cv2.CAP_PROP_FPS)
        if not fps or fps <= 0:
            fps = 30  # fallback seguro

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0

        if end_time is None or end_time <= 0:
            end_time = duration

        if start_time >= end_time:
            raise ValueError(
                "start_time deve ser menor que end_time."
            )

        if start_time >= duration:
            raise ValueError(
                "start_time é maior ou igual à duração do vídeo."
            )

        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)

        # Salto rápido até start_frame usando grab() (não descodifica).
        for _ in range(start_frame):
            if not cap.grab():
                break

        saved_count = 0
        current_frame_index = start_frame

        while current_frame_index <= end_frame:
            ret, frame = cap.read()
            if not ret:
                break

            if (current_frame_index - start_frame) % frame_interval == 0:
                filename = os.path.join(
                    output_dir,
                    f"frame_{saved_count:05d}.{image_format.lower()}",
                )

                if safe_imwrite(filename, frame, jpeg_quality=jpeg_quality):
                    saved_count += 1
                else:
                    logger.warning("Falha ao guardar frame: %s", filename)

            if progress_callback is not None:
                progress_callback(current_frame_index, end_frame)

            current_frame_index += 1

    finally:
        cap.release()

    elapsed = round(time.time() - start_process, 2)

    metadata = {
        "video_name": video_name,
        "output_dir": output_dir,
        "start_time": start_time,
        "end_time": end_time,
        "fps": fps,
        "duration": duration,
        "frames_extracted": saved_count,
        "processing_time": elapsed,
        "image_format": image_format.lower(),
        "frame_interval": frame_interval,
    }

    metadata_path = os.path.join(output_dir, "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)

    return metadata