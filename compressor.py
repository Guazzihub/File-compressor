import os
import subprocess
import hashlib
from pathlib import Path
import concurrent.futures

# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
INPUT_FOLDER = BASE_DIR / "input_files"
PROCESSED_LOG = BASE_DIR / "processed_files.txt"

# Number of files to process concurrently
MAX_WORKERS = 4

# ---------------------------------------------------------------------
# COMPRESSION FUNCTIONS
# (Adjust near-lossless parameters as needed)
# ---------------------------------------------------------------------
def compress_png(file_path: Path):
    """
    Near-lossless PNG using pngquant + optipng
    Example: pngquant --quality=70-90
    """
    temp_output = file_path.with_name(file_path.stem + "-fs8.png")
    subprocess.run([
        "pngquant",
        "--force",
        "--output", str(temp_output),
        "--quality=70-90",
        str(file_path)
    ], check=True)
    subprocess.run(["optipng", "-o7", str(temp_output)], check=True)
    compare_and_replace(file_path, temp_output)

def compress_jpg(file_path: Path):
    """
    Near-lossless JPG compression using 'jpegtran' from libjpeg-turbo.
    '-copy none' removes metadata, '-optimize' optimizes Huffman tables,
    '-perfect' tries lossless if possible.
    """
    temp_output = file_path.with_name(file_path.stem + "_tmp.jpg")
    with open(temp_output, "wb") as stdout_file:
        subprocess.run([
            "jpegtran",
            "-copy", "none",
            "-optimize",
            "-perfect",
            str(file_path)
        ], check=True, stdout=stdout_file)
    compare_and_replace(file_path, temp_output)

def compress_webp(file_path: Path):
    """
    Near-lossless WebP with -q 90
    """
    temp_output = file_path.with_name(file_path.stem + "_tmp.webp")
    subprocess.run([
        "cwebp", "-q", "90",
        str(file_path),
        "-o", str(temp_output)
    ], check=True)
    compare_and_replace(file_path, temp_output)

def compress_gif(file_path: Path):
    """
    GIF optimization using gifsicle -O3
    """
    temp_output = file_path.with_name(file_path.stem + "_opt.gif")
    subprocess.run([
        "gifsicle", "-O3",
        str(file_path),
        "--output", str(temp_output)
    ], check=True)
    compare_and_replace(file_path, temp_output)

def compress_pdf(file_path: Path):
    """
    Near-lossless PDF using Ghostscript:
    -dPDFSETTINGS=/ebook => decent quality, smaller size
    If 'gswin64c' is the name on Windows, replace 'gs' accordingly.
    """
    temp_output = file_path.with_name(file_path.stem + "_compressed.pdf")
    subprocess.run([
        # "gs",  # or "gswin64c" on Windows if that's recognized
        "gswin64c",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/ebook",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={temp_output}",
        str(file_path)
    ], check=True)
    compare_and_replace(file_path, temp_output)

def compress_video(file_path: Path):
    """
    Near-lossless video using FFmpeg (CRF=18, preset=veryslow).
    """
    temp_output = file_path.with_name(file_path.stem + "_tmp" + file_path.suffix)
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(file_path),
        "-c:v", "libx264",
        "-preset", "veryslow",
        "-crf", "18",
        "-c:a", "copy",
        str(temp_output)
    ], check=True)
    compare_and_replace(file_path, temp_output)

# ---------------------------------------------------------------------
# COMPARE AND REPLACE
# ---------------------------------------------------------------------
def compare_and_replace(original_path: Path, new_path: Path):
    """
    If the new file is smaller, replace the original file.
    Otherwise, remove the new file.
    """
    if not new_path.exists():
        return

    old_size = original_path.stat().st_size
    new_size = new_path.stat().st_size

    if new_size < old_size:
        original_path.unlink()
        new_path.rename(original_path)
        print(f"[OK] {original_path.name}: {old_size} => {new_size} bytes")
    else:
        new_path.unlink()
        print(f"[--] {original_path.name} no improvement")

# ---------------------------------------------------------------------
# HASH FUNCTIONS
# ---------------------------------------------------------------------
def get_file_hash(file_path: Path) -> str:
    """
    Compute SHA-1 hash of a file's contents.
    """
    sha1 = hashlib.sha1()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            sha1.update(chunk)
    return sha1.hexdigest()

def is_already_processed(file_hash: str) -> bool:
    """
    Check if a given hash is already in processed_files.txt
    """
    if not PROCESSED_LOG.exists():
        return False
    with open(PROCESSED_LOG, "r") as f:
        for line in f:
            if line.strip() == file_hash:
                return True
    return False

def mark_processed(file_hash: str):
    """
    Append this file's hash to the log so we don't reprocess it.
    """
    with open(PROCESSED_LOG, "a") as f:
        f.write(file_hash + "\n")

# ---------------------------------------------------------------------
# COMPRESS DISPATCH
# ---------------------------------------------------------------------
def compress_file(file_path: Path):
    """
    1) Compute hash first
    2) Check if processed
    3) If not, compress
    4) Then mark processed
    """
    file_hash = get_file_hash(file_path)
    if is_already_processed(file_hash):
        print(f"[SKIP] {file_path.name} (already processed)")
        return

    ext = file_path.suffix.lower()

    if ext == ".png":
        compress_png(file_path)
    elif ext in [".jpg", ".jpeg"]:
        compress_jpg(file_path)
    elif ext == ".webp":
        compress_webp(file_path)
    elif ext == ".gif":
        compress_gif(file_path)
    elif ext == ".pdf":
        compress_pdf(file_path)
    elif ext in [".mp4", ".mov", ".mkv", ".avi"]:
        compress_video(file_path)
    else:
        print(f"[!!] Unsupported extension: {file_path.name}")
        return

    # Only mark as processed after successful compression
    mark_processed(file_hash)

# ---------------------------------------------------------------------
# MAIN (BATCH MODE with concurrency)
# ---------------------------------------------------------------------
def main():
    if not INPUT_FOLDER.exists():
        INPUT_FOLDER.mkdir(parents=True, exist_ok=True)
        print(f"Created folder: {INPUT_FOLDER}")

    # Collect files (non-recursive). 
    # If you want subfolders included, use `rglob("*")` or `glob("**/*")`.
    all_files = [f for f in INPUT_FOLDER.iterdir() if f.is_file()]

    print(f"Found {len(all_files)} files in {INPUT_FOLDER}.")
    print(f"Processing up to {MAX_WORKERS} at a time.\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Map each file to compress_file
        results = list(executor.map(compress_file, all_files))

    print("Done!")

if __name__ == "__main__":
    main()
