# Compressor quase sem Perda

Este projeto oferece um script de compressão em lote **quase sem perda** para imagens (**PNG, JPG, WebP, GIF**), vídeos (**MP4, MOV, MKV, AVI**) e PDFs (apenas no **Windows**).

## Funcionalidades

 1. Uso do **Compressor quase sem Perda**:
   - **PNG**: `pngquant` + `optipng`
   - **JPG**: `jpegtran` (from **libjpeg-turbo**)
   - **WebP**: `cwebp`
   - **GIF**: `gifsicle`
   - **PDF**: `Ghostscript`
   - **Video**: `FFmpeg` (`CRF ~18`)
2. **Ignora arquivos duplicados e já processados** usando hash SHA-1.
3. Suporta **processamento em lote** e **monitoramento em tempo real opcional** (via `watchdog`).
4. Compatível com **Windows**:
   - Instale as ferramentas de linha de comando via **Chocolatey**
   - Instale bibliotecas Python via **pip**

## Requisitos

- **Chocolatey** ([Instruções de Instalação](https://chocolatey.org/install))
- **Python** 3.7+ (certifique-se de que o `pip` esteja disponível)
- A pasta `input_files` deve existir.

## Instalação

1. **Clone** (ou baixe) este repositório.
2. Abra o **Prompt de Comando como Administrador**.
3. **Instale as ferramentas necessárias:**

```cmd
choco install ffmpeg ghostscript pngquant optipng webp gifsicle qpdf libjpeg-turbo -y
```
- **ffmpeg:** Gerencia compressão de vídeos.
- **ghostscript:** Gerencia compressão de PDF.  
- **pngquant + optipng:** Gerencia compressão de PNG.
- **webp (includes cwebp):** Gerencia compressão de imagens WebP.  
- **gifsicle:** Gerencia a compressão de GIFs.  
- **qpdf:** Ferramenta alternativa para PDF. (opcional)
- **libjpeg-turbo:** Fornece o `jpegtran` para compressão de JPG.  

4. **Instale as dependências Python** listadas em `requirements.txt`:
```cmd
pip install -r requirements.txt
```

## Estrutura de Arquivos
```structure
   ├── compressor.py         # Script principal
   ├── requirements.txt      # Dependencias
   ├── processed_files.txt   # Log de arquivos processados
   └── input_files\          # Coloque todos os arquivos que deseja comprimir nessa pasta
```

## Executando o Script

1. Coloque os arquivos em `input_files\`.
2. Execute o comando:
```cmd
python compressor.py
```

## Observações

- Compressão quase sem perda significa que pequenas alterações visuais podem ocorrer, dependendo das configurações de qualidade (ex. `-q 90` para WebP, `-crf 18` para qualidade de vídeos, etc.).
- Arquivos com hash já presente em `processed_files.txt` serão ignorados (para evitar que seja processado novamente).
- Apagar o `processed_files.txt` fará com que todos os arquivos sejam reprocessados.
- Certifique-se de que as ferramentas estão no `PATH` do sistema para serem reconhecidas.

## Como Ativar ou Desativar o Watchdog

O script pode rodar em **dois** modos: em **lote** ou **tempo real**.

### 1. Modo em Lote (Watchdog Desativado)

- **Não importe** ou instale o `watchdog`.  
- **Remova** ou **commente** qualquer código referente ao `Observer`, `FileSystemEventHandler`, ou Modo em Lote (Watchdog Desativado).  
- No  `compressor.py`, faça o loop apenas na pasta `input_files` uma únida vez para compressão dos arquivos.

**Exemplo de snippet (Lote):**
```python
def main():
    if not INPUT_FOLDER.exists():
        INPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    all_files = [f for f in INPUT_FOLDER.iterdir() if f.is_file()]
    print(f"Found {len(all_files)} files.")

    for file_path in all_files:
        compress_file(file_path)

if __name__ == "__main__":
    main()
```

### 2. Modo em Tempo Real (Watchdog Ativado)

- Instale o watchdog (e.g., `pip install watchdog`).
- Importe as classes necessárias:
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
```

**Exemplo de snippet (Tempo Real):**
```python
class CompressionHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        new_file = Path(event.src_path)
        compress_file(new_file)

def main():
    if not INPUT_FOLDER.exists():
        INPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    event_handler = CompressionHandler()
    observer = Observer()
    observer.schedule(event_handler, str(INPUT_FOLDER), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
```

## Como Ajustar os Parâmetros de Compressão

Abaixo estão as funções e parâmetros que você pode ajustar para controlar a **qualidade**. e **tamanho dos arquivos**.
1. **PNG (`compress_png`)**
```python
subprocess.run([
    "pngquant",
    "--force",
    "--output", str(temp_output),
    "--quality=70-90",  # <-- Adjust range for more or less compression
    str(file_path)
], check=True)

subprocess.run(["optipng", "-o7", str(temp_output)], check=True)
```
- **--quality=70-90**: Quanto menor o valor, maior a compressão (e perda).
- **-o7**: Nível de otimização do `optipng` (0-7 sendo que quanto mais alto, mais devagar. O tamanho do arquivo deverá ser menor).

<br>

2. **JPG (`compress_jpg`)**
```python
subprocess.run([
    "jpegtran",
    "-copy", "none",
    "-optimize",
    "-perfect",
    str(file_path)
], check=True)
```
- Nota: O `jpegtran` não reduz a qualidade, apenas otimiza.
- Esses parametros são **quase sem perda.**  

<br>

3. **GIF (`compress_gif`)**
```python
subprocess.run([
    "gifsicle", "-O3",
    str(file_path),
    "--output", str(temp_output)
], check=True)
```
- **-O3** Nível mais alto de otimização do **gifsicle**. Valores menores vão reduzir o tempo de processamento gerando arquivos maiores.

<br>

4. **WebP (`compress_webp`)**
```python
subprocess.run([
    "cwebp", "-q", "90",
    str(file_path),
    "-o", str(temp_output)
], check=True)
```
- **-q 90**: Valores menores geram arquivos menores porém podem significar uma perda considerável na qualidade. (Qualidade de [0–100]).

<br>

5. **PDF (`compress_pdf`)**
```python
subprocess.run([
    "gswin64c",  # or "gs" if installed differently
    "-sDEVICE=pdfwrite",
    "-dCompatibilityLevel=1.4",
    "-dPDFSETTINGS=/ebook",
    ...
], check=True)
```
- **/ebook**: Boa qualidade com tamanho reduzido.  
- **/screen**: Menor tamanho, qualidade mais baixa.
- **/printer**: Alta qualidade, arquivos maiores.

  <br>
  
6. **Vídeo (`compress_video`)**
```python
subprocess.run([
    "ffmpeg", "-y",
    "-i", str(file_path),
    "-c:v", "libx264",
    "-preset", "veryslow",
    "-crf", "18",
    "-c:a", "copy",
    str(temp_output)
], check=True)
```
- **-crf 18**: Menor valor = maior qualidade (arquivos maiores). Faixa comum para baixa perda varia entre 18–23.  
- **-preset veryslow**: Melhor compressão (mais lento). Use `slow` ou `medium` para mais agilidade no processamento.
