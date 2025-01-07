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

- **Chocolatey** installed ([instructions](https://chocolatey.org/install))
- **Python** 3.7+ installed (ensure `pip` is available)
- **Ensure input_files folder exists**

## Installation

1. **Clone** (or download) this repository.
2. Open **Command Prompt** **as Administrator**.
3. **Install the tools listed bellow:**

```cmd
choco install ffmpeg ghostscript pngquant optipng webp gifsicle qpdf libjpeg-turbo -y
```
- **ffmpeg** handles video compression
- **ghostscript** handles PDF compression
- **pngquant + optipng** handle PNG
- **webp (includes cwebp)** handles WebP images
- **gifsicle** handles GIF optimization
- **qpdf** is an alternative PDF tool (optional)
- **libjpeg-turbo** provides jpegtran for JPG optimization

4. **Install Python dependencies from requirements.txt:**
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
- Near-lossless compression means minimal artifacts or changes may occur if quality settings are tweaked (e.g. -q 90 for WebP, -crf 18 in FFmpeg, etc.).
- Any file that matches a previously stored hash in `processed_files.txt` will be skipped (to prevent re-compression).
- Removing or clearing processed_files.txt it can cause reprocessing.
- Make sure the `PATH environment variable` is updated so that the installed tools are recognized.

## How to Enable/Disable Watchdog

By default, the project can run in **two** modes: batch or real-time.

### 1. Batch Mode (Watchdog Disabled)
- **Do not import** or install `watchdog`.  
- **Remove** or **comment out** any code related to `Observer`, `FileSystemEventHandler`, or real-time monitoring.  
- In `compressor.py`, simply loop over `input_files` folder once and compress each file.

Example snippet (batch):
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
- Install watchdog (e.g., pip install watchdog).
- Import the necessary classes:
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
```

Example snippet (real-time):
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
