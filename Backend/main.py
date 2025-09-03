import os
import struct
import math
import string
import hashlib

OUTPUT_DIR = "recovered"
WINDOW_SIZE = 65536
STEP_SIZE = 32768
ENTROPY_THRESHOLD = 7.0
MIN_FILE_SIZE = 1024
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------- SIGNATURES ---------------- #
SIGNATURES = {
    "jpg": {
        "header": b"\xFF\xD8\xFF",
        "footer": b"\xFF\xD9"
    },
    "png": {
        "header": b"\x89PNG\r\n\x1a\n",
        "footer": b"\x49\x45\x4E\x44\xAE\x42\x60\x82"
    },
    "pdf": {
        "header": b"%PDF",
        "footer": b"%%EOF"
    }
}

# Track unique files (avoid duplicates)
seen_hashes = set()

# ---------------- HELPERS ---------------- #
def entropy(data):
    if not data:
        return 0
    counts = [0]*256
    for b in data:
        counts[b] += 1
    ent = 0
    for c in counts:
        if c == 0:
            continue
        p = c / len(data)
        ent -= p * math.log2(p)
    return ent

def sliding_entropy_regions(data, window_size=WINDOW_SIZE, step_size=STEP_SIZE, threshold=ENTROPY_THRESHOLD):
    mv = memoryview(data)
    regions = []
    start = None
    for i in range(0, len(data) - window_size, step_size):
        w = mv[i:i+window_size]
        e = entropy(w)
        if e >= threshold:
            if start is None:
                start = i
        else:
            if start is not None:
                regions.append((start, i+window_size))
                start = None
    if start is not None:
        regions.append((start, len(data)))
    return regions

def file_hash(data):
    return hashlib.sha1(data).hexdigest()

def save_files(file_list, prefix):
    saved = []
    for i, fdata in enumerate(file_list):
        if len(fdata) < MIN_FILE_SIZE:
            continue
        h = file_hash(fdata)
        if h in seen_hashes:
            continue
        seen_hashes.add(h)
        filename = os.path.join(OUTPUT_DIR, f"{prefix}_{len(saved)}.{prefix}")
        with open(filename, "wb") as f:
            f.write(fdata)
        saved.append(filename)
    return saved

# ---------------- RECOVERY FUNCTIONS ---------------- #
def recover_jpg_by_signature(data):
    recovered = []
    sig = SIGNATURES["jpg"]
    header, footer = sig["header"], sig["footer"]
    pos = 0
    while True:
        start = data.find(header, pos)
        if start == -1:
            break
        end = data.find(footer, start)
        if end == -1:
            break
        end += len(footer)
        jpg_data = data[start:end]
        if b"JFIF" in jpg_data[:20] or b"Exif" in jpg_data[:20]:
            if len(jpg_data) >= MIN_FILE_SIZE:
                recovered.append(jpg_data)
        pos = end
    return recovered

def recover_png(data):
    recovered = []
    pos = 0
    header = SIGNATURES["png"]["header"]
    footer = SIGNATURES["png"]["footer"]

    while True:
        start = data.find(header, pos)
        if start == -1:
            break

        end = data.find(footer, start)
        if end != -1:
            candidate = data[start:end+len(footer)]
            if len(candidate) >= MIN_FILE_SIZE:
                recovered.append(candidate)
                pos = end + len(footer)
                continue

        # Structural recovery
        offset = start + len(header)
        last_good = offset
        found_iend = False

        while offset + 8 <= len(data):
            try:
                length = struct.unpack(">I", data[offset:offset+4])[0]
                chunk_type = data[offset+4:offset+8]
                if length < 0 or length > 50_000_000 or offset + 12 + length > len(data):
                    break
                offset += 8 + length + 4
                last_good = offset
                if chunk_type == b"IEND":
                    found_iend = True
                    break
            except Exception:
                break

        if found_iend:
            candidate = data[start:offset]
            if len(candidate) >= MIN_FILE_SIZE:
                recovered.append(candidate)
        else:
            truncated = data[start:last_good]
            if len(truncated) >= MIN_FILE_SIZE:
                recovered.append(truncated)

        pos = start + 8
    return recovered

# ---------------- PDF RECOVERY ---------------- #
# ---------------- PDF RECOVERY (robust) ---------------- #
# ---------------- PDF RECOVERY (robust) ---------------- #
def recover_pdf(data):
    recovered = []
    hdr = SIGNATURES["pdf"]["header"]
    eof = SIGNATURES["pdf"]["footer"]
    pos = 0
    n = len(data)
    MAX_PDF_SIZE = 50 * 1024 * 1024  # 50MB cap for safety
    MIN_FILE_SIZE = 1024

    while True:
        start = data.find(hdr, pos)
        if start == -1:
            break

        # Look for the nearest EOF after start
        end = data.find(eof, start)
        if end != -1:
            end += len(eof)
        else:
            # No EOF found → use max size cap
            end = min(start + MAX_PDF_SIZE, n)

        pdf_data = data[start:end]

        if len(pdf_data) >= MIN_FILE_SIZE:
            recovered.append(pdf_data)

        # Move pointer past this PDF to avoid duplicates
        pos = end

    return recovered



def recover_wav(data):
    recovered = []
    pos = 0
    while True:
        riff = data.find(b"RIFF", pos)
        if riff == -1:
            break
        if data[riff+8:riff+12] == b"WAVE":
            size_bytes = data[riff+4:riff+8]
            if len(size_bytes) < 4:
                break
            size = struct.unpack("<I", size_bytes)[0] + 8
            end = riff + size
            wav_data = data[riff:end]
            if len(wav_data) >= MIN_FILE_SIZE:
                recovered.append(wav_data)
            pos = end
        else:
            pos += 4
    return recovered

def extract_text(data, min_length=200, max_files=2):
    printable = set(bytes(string.printable, 'ascii'))
    results = []
    current = b""
    for byte in data:
        if byte in printable:
            current += bytes([byte])
        else:
            if len(current) >= min_length:
                results.append(current)
            current = b""
    if len(current) >= min_length:
        results.append(current)
    return sorted(results, key=len, reverse=True)[:max_files]

# ---------------- MAIN ---------------- #
if __name__ == "__main__":
    disk_image = "leo_disk.img"
    with open(disk_image, "rb") as f:
        data = f.read()

    recovered_count = 0

    print("[*] Recovering JPG files...")
    jpg_files = save_files(recover_jpg_by_signature(data), "jpg")
    recovered_count += len(jpg_files)

    print("[*] Recovering PNG files...")
    png_files = save_files(recover_png(data), "png")
    recovered_count += len(png_files)

    print("[*] Recovering PDF files...")
    pdf_files = save_files(recover_pdf(data), "pdf")
    recovered_count += len(pdf_files)

    print("[*] Recovering WAV files...")
    wav_files = save_files(recover_wav(data), "wav")
    recovered_count += len(wav_files)

    print("[*] Recovering TXT files...")
    txt_files = save_files(extract_text(data, 200, 2), "txt")
    recovered_count += len(txt_files)

    print(f"\n[+] Done! Total recovered files: {recovered_count}")
    print(f"JPG: {len(jpg_files)}, PNG: {len(png_files)}, PDF: {len(pdf_files)}, WAV: {len(wav_files)}, TXT: {len(txt_files)}")
