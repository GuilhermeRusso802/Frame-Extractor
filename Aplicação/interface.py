import threading
import os

import customtkinter as ctk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image

from extractor import extract_frames

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    """
    Aplicação gráfica para extração de frames de vídeos.

    Permite:
        - Selecionar vídeos.
        - Definir intervalo de extração.
        - Escolher intervalo temporal (slider + input manual).
        - Pré-visualizar frames.
        - Extrair frames para uma pasta definida pelo utilizador
          numa thread separada, com barra de progresso.
    """

    def __init__(self):
        """
        Inicializa a interface gráfica e todos os componentes da aplicação.
        """
        super().__init__()

        self.title("Video Frame Extractor")
        self.geometry("900x780")
        self.resizable(True, True)

        self.video_path = None
        self.output_path = None
        self.video_duration = 0
        self.cap = None
        self._extracting = False

        self.main_frame = ctk.CTkScrollableFrame(
            self, width=850, height=720
        )
        self.main_frame.pack(
            fill="both", expand=True, padx=20, pady=20
        )

        ctk.CTkLabel(
            self.main_frame,
            text="Extrator de Frames",
            font=("Arial", 26, "bold"),
        ).pack(pady=20)

        ctk.CTkButton(
            self.main_frame,
            text="Selecionar Vídeo",
            command=self.select_video,
            width=250,
        ).pack(pady=10)

        self.video_label = ctk.CTkLabel(
            self.main_frame, text="Nenhum vídeo selecionado"
        )
        self.video_label.pack()

        self.preview_label = ctk.CTkLabel(self.main_frame, text="")
        self.preview_label.pack(pady=20)

        ctk.CTkLabel(
            self.main_frame, text="Intervalo entre frames"
        ).pack()
        self.interval_entry = ctk.CTkEntry(self.main_frame, width=100)
        self.interval_entry.insert(0, "30")
        self.interval_entry.pack(pady=10)

        ctk.CTkLabel(self.main_frame, text="Tempo Inicial").pack()
        self.start_time_entry = ctk.CTkEntry(self.main_frame, width=120)
        self.start_time_entry.pack(pady=5)
        self.start_time_entry.insert(0, "00:00:00")
        self.start_time_entry.bind(
            "<Return>", self.update_start_from_entry
        )

        self.start_slider = ctk.CTkSlider(
            self.main_frame,
            from_=0,
            to=100,
            command=self.update_start_label,
        )
        self.start_slider.pack(pady=10, padx=50, fill="x")

        ctk.CTkLabel(self.main_frame, text="Tempo Final").pack()
        self.end_time_entry = ctk.CTkEntry(self.main_frame, width=120)
        self.end_time_entry.pack(pady=5)
        self.end_time_entry.insert(0, "00:00:00")
        self.end_time_entry.bind(
            "<Return>", self.update_end_from_entry
        )

        self.end_slider = ctk.CTkSlider(
            self.main_frame,
            from_=0,
            to=100,
            command=self.update_end_label,
        )
        self.end_slider.set(100)
        self.end_slider.pack(pady=10, padx=50, fill="x")

        ctk.CTkButton(
            self.main_frame,
            text="Selecionar Output",
            command=self.select_output,
            width=250,
        ).pack(pady=10)

        self.output_label = ctk.CTkLabel(
            self.main_frame, text="Selecione uma pasta para output."
        )
        self.output_label.pack()

        self.extract_button = ctk.CTkButton(
            self.main_frame,
            text="Extrair Frames",
            command=self.run_extraction,
            width=250,
            height=40,
        )
        self.extract_button.pack(pady=20)

        self.progress_bar = ctk.CTkProgressBar(
            self.main_frame, width=400
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

        self.status_label = ctk.CTkLabel(self.main_frame, text="")
        self.status_label.pack()

    def format_time(self, seconds) -> str:
        """
        Converte tempo em segundos para formato legível HH:MM:SS.
        """
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02}:{minutes:02}:{secs:02}"

    def parse_time(self, time_string: str) -> int:
        """
        Converte uma string no formato HH:MM:SS para segundos.

        Raises:
            ValueError: se o formato não for válido.
        """
        try:
            h, m, s = map(int, time_string.split(":"))
            return h * 3600 + m * 60 + s
        except (ValueError, AttributeError):
            raise ValueError("Formato inválido. Use HH:MM:SS")

    def select_video(self):
        """
        Abre um explorador de ficheiros para selecionar um vídeo.
        """
        path = filedialog.askopenfilename(
            filetypes=[("Vídeos", "*.mp4 *.avi *.mov *.mkv")]
        )
        if not path:
            return

        self.video_path = path
        self.video_label.configure(text=os.path.basename(path))

        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(path)
        self.load_preview()

    def select_output(self):
        """
        Abre um diálogo para selecionar a pasta de output.
        """
        path = filedialog.askdirectory()
        if path:
            self.output_path = path
            self.output_label.configure(text=f"Output: {path}")

    def load_preview(self):
        """
        Carrega informações do vídeo selecionado e mostra o primeiro frame.
        """
        fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        self.video_duration = total_frames / fps if fps else 0

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = self.cap.read()
        if ret:
            self.display_frame(frame)

        self.start_slider.configure(to=self.video_duration)
        self.end_slider.configure(to=self.video_duration)
        self.start_slider.set(0)
        self.end_slider.set(self.video_duration)

        self._set_entry(self.start_time_entry, self.format_time(0))
        self._set_entry(
            self.end_time_entry, self.format_time(self.video_duration)
        )

    def display_frame(self, frame):
        """
        Mostra um frame do vídeo na interface gráfica.

        Converte o frame de OpenCV (BGR) para RGB e ajusta para preview.
        """
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        image.thumbnail((500, 350))

        ctk_image = ctk.CTkImage(
            light_image=image, dark_image=image, size=image.size
        )
        self.preview_label.configure(image=ctk_image, text="")
        # Mantém referência para evitar garbage collection.
        self.preview_label.image = ctk_image

    def update_preview_frame(self, timestamp):
        """
        Atualiza o frame exibido com base num timestamp em segundos.
        """
        if not self.cap:
            return

        fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        target_frame = int(timestamp * fps)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)

        ret, frame = self.cap.read()
        if ret:
            self.display_frame(frame)

    @staticmethod
    def _set_entry(entry, value: str):
        """Substitui o texto de um CTkEntry."""
        entry.delete(0, "end")
        entry.insert(0, value)

    def _update_from_slider(self, entry, value):
        """Atualiza o entry e o preview quando o slider muda."""
        self._set_entry(entry, self.format_time(value))
        self.update_preview_frame(value)

    def _update_from_entry(self, slider, entry):
        """Atualiza o slider e o preview a partir do entry (HH:MM:SS)."""
        try:
            seconds = self.parse_time(entry.get())
            seconds = max(0, min(seconds, self.video_duration))
            slider.set(seconds)
            self.update_preview_frame(seconds)
        except ValueError:
            messagebox.showerror(
                "Erro", "Formato inválido. Use HH:MM:SS"
            )

    def update_start_label(self, value):
        self._update_from_slider(self.start_time_entry, value)

    def update_end_label(self, value):
        self._update_from_slider(self.end_time_entry, value)

    def update_start_from_entry(self, event=None):
        self._update_from_entry(self.start_slider, self.start_time_entry)

    def update_end_from_entry(self, event=None):
        self._update_from_entry(self.end_slider, self.end_time_entry)

    def run_extraction(self):
        """
        Valida entradas e dispara a extração de frames numa thread separada.
        """
        if self._extracting:
            return

        if not self.video_path:
            messagebox.showerror(
                "Erro", "Seleciona um vídeo primeiro."
            )
            return

        if not self.output_path:
            messagebox.showerror(
                "Erro", "Seleciona uma pasta de output primeiro."
            )
            return

        try:
            interval = int(self.interval_entry.get())
        except ValueError:
            messagebox.showerror("Erro", "Intervalo inválido.")
            return

        start_time = self.start_slider.get()
        end_time = self.end_slider.get()

        if start_time >= end_time:
            messagebox.showerror(
                "Erro",
                "Tempo inicial deve ser menor que tempo final.",
            )
            return

        self._extracting = True
        self.extract_button.configure(state="disabled")
        self.progress_bar.set(0)
        self.status_label.configure(text="A extrair frames...")

        thread = threading.Thread(
            target=self._extract_worker,
            args=(
                self.video_path,
                self.output_path,
                interval,
                start_time,
                end_time,
            ),
            daemon=True,
        )
        thread.start()

    def _extract_worker(
        self, video_path, output_path, interval, start_time, end_time
    ):
        """
        Executa extract_frames numa thread de fundo.

        Comunica de volta com a GUI através de self.after(0, ...), porque
        o Tkinter não é thread-safe.
        """
        try:
            result = extract_frames(
                video_path=video_path,
                output_dir=output_path,
                frame_interval=interval,
                start_time=start_time,
                end_time=end_time,
                progress_callback=self._on_progress,
            )
            self.after(0, lambda: self._on_extraction_done(result))
        except Exception as e:
            self.after(0, lambda: self._on_extraction_error(e))

    def _on_progress(self, current, total):
        """Callback chamado pela função de extração (em background thread)."""
        if total <= 0:
            return
        ratio = max(0.0, min(1.0, current / total))
        self.after(0, lambda: self.progress_bar.set(ratio))

    def _on_extraction_done(self, result):
        self._extracting = False
        self.extract_button.configure(state="normal")
        self.progress_bar.set(1.0)
        self.status_label.configure(text="Extração concluída.")
        messagebox.showinfo(
            "Sucesso",
            (
                f"Frames extraídos: {result['frames_extracted']}\n"
                f"Tempo de processamento: {result['processing_time']}s"
            ),
        )

    def _on_extraction_error(self, error):
        self._extracting = False
        self.extract_button.configure(state="normal")
        self.progress_bar.set(0)
        self.status_label.configure(text="Erro na extração.")
        messagebox.showerror("Erro", str(error))

    def on_closing(self):
        if self.cap:
            self.cap.release()
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()