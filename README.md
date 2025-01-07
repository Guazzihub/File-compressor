# Near-Lossless Bulk Compressor

This project provides a **near-lossless** bulk compression script for images (PNG, JPG, WebP, GIF), videos (MP4, MOV, MKV, AVI), and PDFs on **Windows** systems. It uses various command-line tools (installed via Chocolatey) and Python (with some optional libraries from `requirements.txt`).

## Features

1. **Near-lossless compression** using:
   - **PNG**: `pngquant` + `optipng`
   - **JPG**: `jpegtran` from **libjpeg-turbo**
   - **WebP**: `cwebp`
   - **GIF**: `gifsicle`
   - **PDF**: `Ghostscript`
   - **Video**: `FFmpeg` (CRF ~18)
2. **Skips re-processing** of duplicate files by hashing (SHA-1).
3. **Optional** real-time folder monitoring using `watchdog`.
4. **Windows-friendly** setup:
   - Installs command-line tools via **Chocolatey**.
   - Installs Python libraries via **pip**.

## Requirements

- **Windows** 10 or 11
- **Chocolatey** installed ([instructions](https://chocolatey.org/install))
- **Python** 3.7+ installed (make sure `pip` is available)

## Installation

1. **Clone or download** this repository.
2. Open **PowerShell** or **Command Prompt** in **Administrator mode**.

3. **Install command-line tools** via Chocolatey:
   ```powershell
   choco install ffmpeg ghostscript pngquant optipng webp gifsicle qpdf libjpeg-turbo -y
Note:

ffmpeg handles video compression.
ghostscript handles PDF compression.
pngquant and optipng handle PNG.
webp (includes cwebp) handles WebP images.
gifsicle handles GIF optimization.
qpdf is an alternative PDF tool (optional).
libjpeg-turbo provides jpegtran for JPG optimization.
Install Python dependencies from requirements.txt:

powershell
Copiar código
pip install -r requirements.txt
Folder structure (example):

makefile
Copiar código
C:\
 └── compressor\
      ├── compressor.py         # The main Python script
      ├── requirements.txt      # Python dependencies
      ├── processed_files.txt   # Log for processed files (optional, can be empty at first)
      └── input_files\          # Put all the files you want to compress here
Run the script:

powershell
Copiar código
python compressor.py
If you are using the watchdog version, the script will monitor input_files\ for new files in real time.
If you use a batch version, it will scan and compress existing files once.
Usage
Place the files you want to compress inside input_files\.
Check the console output to see the compression results.
Any file that is already processed (duplicate hash) will be skipped automatically.
Notes
The compression is near-lossless—some minimal artifacts or changes may occur if you tweak quality settings (e.g., -q 90 for WebP or -crf 18 in FFmpeg).
processed_files.txt is used to store the file hashes (SHA-1). If you remove it, the script may reprocess the same files again.
Make sure your PATH environment variable is updated to point to the installed tools (Chocolatey should handle this by default, but a terminal refresh or system restart might be required).