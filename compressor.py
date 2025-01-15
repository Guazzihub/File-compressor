import os
import subprocess
import hashlib
from pathlib import Path
import concurrent.futures

# CONFIG
BASE_DIR = Path(__file__).resolve().parent
INPUT_FOLDER = BASE_DIR / "input_files"
PROCESSED_LOG = BASE_DIR / "processed_files.txt"

# Queue size
MAX_WORKERS = 4

# COMPRESSION
def compress_png(file_path: Path):
    temp_output = file_path.with_name(file_path.stem + "-fs8.png")
    subprocess.run([
        "pngquant",
        "--force",
        "--output", str(temp_output),
        "--quality=50-70",  # PNG Settings
        str(file_path)
    ], check=True)
    subprocess.run(["optipng", "-o7", str(temp_output)], check=True)
    compare_and_replace(file_path, temp_output)

def compress_jpg(file_path: Path):
    temp_output = file_path.with_name(file_path.stem + "_tmp.jpg")
    with open(temp_output, "wb") as stdout_file:
        subprocess.run([
            "jpegtran",       # JPEG Settings
            "-copy", "none",  # Remove metadata
            "-optimize",      # Optimize Huffman tables
            "-progressive",   # Progressive compression
            "-perfect",
            str(file_path)
        ], check=True, stdout=stdout_file)
    compare_and_replace(file_path, temp_output)

def compress_webp(file_path: Path):
    temp_output = file_path.with_name(file_path.stem + "_tmp.webp")
    subprocess.run([
        "cwebp", "-q", "60",  # WEBP Settings
        str(file_path),
        "-o", str(temp_output)
    ], check=True)
    compare_and_replace(file_path, temp_output)

def compress_gif(file_path: Path):
    temp_output = file_path.with_name(file_path.stem + "_opt.gif")

    subprocess.run([
        "gifsicle",
        "-O3",                   # GIF Settings
        "--colors", "32",        # Reduce color palette
        "--resize-width", "75%", # Optional
        str(file_path),
        "--output", str(temp_output)
    ], check=True)

    compare_and_replace(file_path, temp_output)

def compress_pdf(file_path: Path):
    temp_output = file_path.with_name(file_path.stem + "_compressed.pdf")
    subprocess.run([
        "gswin64c",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/screen",  # PDF Settings
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={temp_output}",
        str(file_path)
    ], check=True)
    compare_and_replace(file_path, temp_output)

def compress_video(file_path: Path):
    temp_output = file_path.with_name(file_path.stem + "_tmp" + file_path.suffix)
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(file_path),
        "-c:v", "libx264",
        "-preset", "slow",   # Video Settings
        "-crf", "23",        # Quality
        "-c:a", "aac",
        "-b:a", "96k",       # Audio bitrate
        str(temp_output)
    ], check=True)
    compare_and_replace(file_path, temp_output)

def compare_and_replace(original_path: Path, new_path: Path):
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
        print(f"[--] {original_path.name} No Improvement")

def get_file_hash(file_path: Path) -> str:
    sha1 = hashlib.sha1() # Hashing
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha1.update(chunk)
    return sha1.hexdigest()

def is_already_processed(file_hash: str) -> bool:
    if not PROCESSED_LOG.exists():
        return False
    with open(PROCESSED_LOG, "r") as f:
        return file_hash in {line.strip() for line in f}

def mark_processed(file_hash: str):
    with open(PROCESSED_LOG, "a") as f:
        f.write(file_hash + "\n")

def compress_file(file_path: Path):
    file_hash = get_file_hash(file_path)
    if is_already_processed(file_hash):
        print(f"[SKIP] {file_path.name} (Processed)")
        return

    ext = file_path.suffix.lower()
    try:
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
            print(f"[!!] Not supported: {file_path.name}")
            return
        mark_processed(file_hash)
    except Exception as e:
        print(f"[ERROR] {file_path.name}: {e}")

# MAIN
def main():
    if not INPUT_FOLDER.exists():
        INPUT_FOLDER.mkdir(parents=True, exist_ok=True)
        print(f"Pasta criada: {INPUT_FOLDER}")

    all_files = [f for f in INPUT_FOLDER.iterdir() if f.is_file()]

    print(f"{len(all_files)} found in {INPUT_FOLDER}.")
    print(f"Processing {MAX_WORKERS} files...\n")

    # Parallel processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(compress_file, all_files)

    print("Done!")

if __name__ == "__main__":
    main()
