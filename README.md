# Near-Lossless Bulk Compressor

This project provides a **near-lossless** bulk compression script for images (**PNG, JPG, WebP, GIF**), videos (**MP4, MOV, MKV, AVI**), and PDFs on **Windows**.

## Features

 1. **Near-lossless compression** using:
   - **PNG**: `pngquant` + `optipng`
   - **JPG**: `jpegtran` (from **libjpeg-turbo**)
   - **WebP**: `cwebp`
   - **GIF**: `gifsicle`
   - **PDF**: `Ghostscript`
   - **Video**: `FFmpeg` (`CRF ~18`)
2. **Skips re-processing** of duplicate files by hashing (SHA-1).
3. Supports either **batch processing** and **optional** real-time monitoring (via `watchdog`).
4. **Windows-friendly**:
   - Installs CLI tools via **Chocolatey**.
   - Installs Python libraries via **pip**.

## Requirements

- **Chocolatey** ([Instructions](https://chocolatey.org/install)).
- **Python** 3.7+ (ensure `pip` is available).
- **Ensure input_files folder exists**.

## Installation

1. **Clone** (or download) this repository.
2. Open **Command Prompt** **as Administrator**.
3. **Install the tools listed below:**

```cmd
choco install ffmpeg ghostscript pngquant optipng webp gifsicle qpdf libjpeg-turbo -y
```
- **ffmpeg:** handles video compression.
- **ghostscript:** handles PDF compression. 
- **pngquant + optipng:** handle PNG compression.
- **webp (includes cwebp):** handles WebP compression. 
- **gifsicle:** handles GIF compression.
- **qpdf:** is an alternative PDF tool. (optional)
- **libjpeg-turbo:** provides `jpegtran` for JPG compression.  

4. **Install Python dependencies** from `requirements.txt`:
```cmd
pip install -r requirements.txt
```

## Folder Structure
```structure
   ├── compressor.py         # Main
   ├── requirements.txt      # Dependencies
   ├── processed_files.txt   # Log processed files
   └── input_files\          # Put all the files you want to compress here
```

## Running the Script

1. Place files in `input_files\`.
2. Run:
```cmd
python compressor.py
```

## Notes

- Near-lossless compression means minimal artifacts or changes may occur if quality settings are tweaked (e.g. `-q 90` for WebP, `-crf 18` in FFmpeg, etc.).
- Any file that matches a previously stored hash in `processed_files.txt` will be skipped (to prevent re-compression).
- Removing or clearing `processed_files.txt` can cause reprocessing.
- Make sure the `PATH` environment variable is updated so that the installed tools are recognized.

## How to Enable/Disable Watchdog

By default, the project can run in **two** modes: batch or real-time.

### 1. Batch Mode (Watchdog Disabled)

- **Do not import** or install `watchdog`.  
- **Remove** or **comment out** any code related to `Observer`, `FileSystemEventHandler`, or real-time monitoring.  
- In `compressor.py`, simply loop over `input_files` folder once and compress each file.

**Example snippet (batch):**
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

### 2. Real-Time Mode (Watchdog Enabled)

- Install watchdog (e.g., `pip install watchdog`).
- Import the necessary classes:
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
```

**Example snippet (real-time):**
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

## How to Change Compression Parameters

Below are the **key functions** and parameters you can modify for **near-lossless compression**. Adjust them according to your desired trade-off between **file size** and **quality**.

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
- **--quality=70-90**: Lower the first number for smaller files (with slightly more noticeable compression).  
- **-o7**: `optipng` optimization level (0–7). Higher is slower but may yield smaller files.

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
- These parameters are **near-lossless**.  
- If you want to reduce quality further, consider using `jpegoptim --max=85` or switching tools.  
- Note that `jpegtran` in this mode does not reduce quality; it only optimizes.

<br>

3. **GIF (`compress_gif`)**
```python
subprocess.run([
    "gifsicle", "-O3",
    str(file_path),
    "--output", str(temp_output)
], check=True)
```
- **-O3** is the highest optimization level for **gifsicle**. Lower might save time but produce a larger file.

<br>

4. **WebP (`compress_webp`)**
```python
subprocess.run([
    "cwebp", "-q", "90",
    str(file_path),
    "-o", str(temp_output)
], check=True)
```
- **-q 90**: The quality factor (0–100). Lower is smaller but might introduce artifacts.

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
- **/ebook**: Good balance of size and quality.  
- **/screen**: Smaller files, lower quality  
- **/printer**: Larger files, higher quality

  <br>
  
6. **Video (`compress_video`)**
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
- **-crf 18**: Lower CRF means higher quality (and bigger files). Around 18–23 is typical for near-lossless.  
- **-preset veryslow**: Slower encoding but more efficient compression. You can switch to `slow` or `medium` for faster encodes at a slight cost in size.
