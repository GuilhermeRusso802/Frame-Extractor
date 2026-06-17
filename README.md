[README.md](https://github.com/user-attachments/files/28018208/README.md)

# Extrator de Frames

Ferramenta modular para extração e pré-processamento de frames de vídeo,
desenvolvida no âmbito de um projeto de estágio curricular focado em
**análise de saúde de peixes em aquacultura**.

A aplicação permite selecionar um vídeo, definir um intervalo temporal e a
frequência de extração, e produzir uma sequência de frames organizados em
disco, juntamente com um ficheiro de *metadata* que descreve o processamento.
O resultado pode ser usado diretamente como entrada para pipelines de visão
computacional posteriores.

O componente foi desenhado para ser **autónomo e reutilizável**: o módulo
`extractor.py` pode ser importado por outros projetos, e duas interfaces
distintas (GUI e CLI) consomem essa mesma API.

---

## Funcionalidades

- Interface gráfica moderna baseada em [CustomTkinter](https://customtkinter.tomschimansky.com/).
- Interface de linha de comandos (CLI) equivalente à GUI.
- Extração de frames com intervalo configurável (1 frame a cada *N*).
- Recorte temporal do vídeo (`start_time` / `end_time` em segundos).
- Pré-visualização do frame correspondente à posição do slider.
- Suporte a JPEG (com qualidade configurável) e PNG.
- Geração automática de `metadata.json` com informação do processamento.
- Organização dos outputs em pastas por execução (com timestamp).
- Extração em *background thread* na GUI, com barra de progresso.
- Tratamento robusto de caminhos com caracteres não-ASCII (acentos, cedilhas).

---

## Formatos de vídeo suportados

Os formatos suportados dependem dos *codecs* instalados no sistema. Foram
testados:

- `.mp4` (recomendado)
- `.avi`
- `.mov`
- `.mkv` (dependente de *codec*)

---

## Compatibilidade

- Windows 10/11
- macOS
- Linux

Em macOS pode ser necessário instalar o FFmpeg para melhor compatibilidade
com determinados *codecs* de vídeo:

```bash
brew install ffmpeg
```

---

## Estrutura do projeto

```
Aplicação/
├── interface.py        # Interface gráfica (GUI)
├── main.py             # Interface de linha de comandos (CLI)
├── extractor.py        # Lógica de extração (módulo reutilizável)
├── requirements.txt    # Dependências
├── README.md
└── Application.exe     # Executável (gerado via PyInstaller)
```

---

## Instalação

A forma mais simples de utilizar a aplicação é abrir o executável
`Application.exe`, sem qualquer instalação adicional.

Para uso a partir do código-fonte (modificação, execução via CLI, ou
integração com outros projetos), siga os passos abaixo no terminal:

### 1. Clonar / copiar o projeto

```bash
cd caminho/para/Aplicação
```

### 2. (Recomendado) Criar ambiente virtual

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

---

## Uso da Interface Gráfica (GUI)

```bash
python interface.py
```

Fluxo típico:

1. Clicar em **Selecionar Vídeo** e escolher o ficheiro de entrada.
2. Definir o intervalo entre frames (por defeito, 30).
3. Ajustar **Tempo Inicial** e **Tempo Final** usando os *sliders* ou
   introduzindo manualmente no formato `HH:MM:SS`.
4. Clicar em **Selecionar Output** e escolher a pasta de destino.
5. Clicar em **Extrair Frames**.

Durante a extração a barra de progresso é atualizada e a aplicação
mantém-se responsiva (extração corre em *thread* separada).

---

## Uso da Linha de Comandos (CLI)

Exemplo mínimo:

```bash
python main.py --video video.mp4 --output outputs --interval 30
```

Exemplo completo:

```bash
python main.py \
    --video video.mp4 \
    --output outputs \
    --interval 15 \
    --start-time 10 \
    --end-time 60 \
    --image-format jpg \
    --jpeg-quality 95
```

### Argumentos disponíveis

| Argumento         | Tipo    | Default   | Descrição                                       |
|-------------------|---------|-----------|-------------------------------------------------|
| `--video`         | str     | *(obrig)* | Caminho do vídeo de entrada                     |
| `--output`        | str     | `outputs` | Pasta de saída                                  |
| `--interval`      | int     | `30`      | Extrair 1 frame a cada *N*                      |
| `--start-time`    | float   | `0`       | Tempo inicial em segundos                       |
| `--end-time`      | float   | *(fim)*   | Tempo final em segundos                         |
| `--image-format`  | str     | `jpg`     | Formato das imagens: `jpg` ou `png`             |
| `--jpeg-quality`  | int     | `95`      | Qualidade JPEG (1–100)                          |

Nota: O argumento 'jpeg-quality' é incompatível com o formato de imagem 'png'
---

## Uso como biblioteca

O módulo `extractor.py` pode ser importado diretamente em pipelines de
análise. A função `extract_frames` aceita ainda um *callback* opcional para
reportar progresso:

```python
from extractor import extract_frames

def on_progress(current, total):
    print(f"{current}/{total}")

metadata = extract_frames(
    video_path="video.mp4",
    output_dir="outputs",
    frame_interval=30,
    start_time=0,
    end_time=60,
    image_format="jpg",
    jpeg_quality=95,
    progress_callback=on_progress,
)

print(metadata["frames_extracted"], "frames extraídos.")
```

### Assinatura

```python
extract_frames(
    video_path: str,
    output_dir: str,
    frame_interval: int = 30,
    start_time: float = 0,
    end_time: float | None = None,
    image_format: str = "jpg",
    jpeg_quality: int = 95,
    progress_callback: Callable[[int, int], None] | None = None,
) -> dict
```

### Exceções

- `FileNotFoundError` — vídeo não existe.
- `ValueError` — parâmetros inválidos (intervalo ≤ 0, `start_time` fora de
  limites, formato não suportado, vídeo não abre).

---

## Estrutura do output

Cada execução cria uma subpasta dentro de `output_dir`, identificada pelo
nome do vídeo e *timestamp*:

```
outputs/
└── video_20260519_153045/
    ├── frame_00000.jpg
    ├── frame_00001.jpg
    ├── ...
    └── metadata.json
```

### Conteúdo de `metadata.json`

```json
{
    "video_name": "video",
    "output_dir": "outputs/video_20260519_153045",
    "start_time": 0,
    "end_time": 60.0,
    "fps": 29.97,
    "duration": 120.5,
    "frames_extracted": 120,
    "processing_time": 4.32,
    "image_format": "jpg",
    "frame_interval": 15
}
```

---

## Gerar o executável com PyInstaller

Para produzir `Application.exe` a partir do código-fonte:

```bash
python -m pip install pyinstaller
python -m Pyinstaller --onefile --windowed --name Application interface.py
```

O executável é gerado em `dist/Application.exe`. A flag `--windowed` evita
que se abra uma janela de terminal ao executar a GUI.

---

## Tecnologias

**Dependências externas**

- [OpenCV](https://opencv.org/) — leitura de vídeo e codificação de frames.
- [CustomTkinter](https://customtkinter.tomschimansky.com/) — *widgets*
  modernos para a GUI.
- [Pillow](https://python-pillow.org/) — conversão de frames para o
  *preview* da GUI.

**Biblioteca padrão**

- `argparse`, `json`, `logging`, `threading`, `datetime`, `os`, `time`.

**Empacotamento**

- [PyInstaller](https://pyinstaller.org/) — geração do executável.

**Requisito mínimo**

- Python 3.10 ou superior.

---

## Contexto académico

Este projeto foi desenvolvido no âmbito de um estágio curricular na
**Universidade Portucalense (UPT)**, como componente modular de apoio a um
projeto mais amplo de **análise automática de vídeo em aquacultura para
avaliação da saúde dos peixes**. O foco é fornecer uma camada de
infraestrutura — extração, pré-processamento e organização estruturada
de dados — independente do trabalho de modelação, mas com interfaces
suficientemente claras para ser integrada em fluxos de análise
posteriores.









