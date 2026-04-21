import tkinter as tk
from tkinter import filedialog, messagebox
import os

from extractor import extract_frames


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("Video Frame Extractor")
        self.root.geometry("500x380")

        self.video_path = ""
        self.output_path = "outputs"

        tk.Label(
            root,
            text="Video Frame Extractor",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        tk.Button(
            root,
            text="Selecionar Vídeo",
            command=self.select_video,
            width=25
        ).pack(pady=5)

        self.video_label = tk.Label(
            root,
            text="Nenhum vídeo selecionado",
            fg="blue",
            wraplength=450
        )
        self.video_label.pack(pady=5)

        tk.Button(
            root,
            text="Selecionar Pasta Output",
            command=self.select_output,
            width=25
        ).pack(pady=5)

        self.output_label = tk.Label(
            root,
            text="Output: outputs",
            fg="green",
            wraplength=450
        )
        self.output_label.pack(pady=5)

        tk.Label(root, text="Intervalo (frames)").pack(pady=5)

        self.interval = tk.Entry(root, width=10)
        self.interval.insert(0, "30")
        self.interval.pack()

        tk.Button(
            root,
            text="Extrair Frames",
            command=self.run,
            bg="#4CAF50",
            fg="white",
            width=20
        ).pack(pady=20)

    def select_video(self):
        path = filedialog.askopenfilename(
            filetypes=[
                ("Vídeos", "*.mp4 *.avi *.mov *.mkv"),
                ("Todos", "*.*")
            ]
        )

        if path:
            self.video_path = path
            filename = os.path.basename(path)

            self.video_label.config(
                text=f"Vídeo: {filename}"
            )

    def select_output(self):
        path = filedialog.askdirectory()

        if path:
            self.output_path = path

            self.output_label.config(
                text=f"Output: {path}"
            )

    def run(self):

        if not self.video_path:
            messagebox.showerror(
                "Erro",
                "Seleciona um vídeo primeiro."
            )
            return

        try:
            interval = int(self.interval.get())

            result = extract_frames(
                video_path=self.video_path,
                output_dir=self.output_path,
                frame_interval=interval
            )

            messagebox.showinfo(
                "Sucesso",
                f"Frames extraídos: {result['frames_extracted']}"
            )

        except Exception as e:
            messagebox.showerror("Erro", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()