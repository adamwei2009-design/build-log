"""Remove hidden metadata chunks from a PNG without touching the pixels.

Some tools add a content-credentials (C2PA) chunk called caBX, plus text
chunks. Social sites may then show a label on the image. This keeps only
the chunks needed to draw the picture.

Usage: python strip_png_metadata.py in.png out.png
"""
import struct
import sys
import zlib

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
KEEP = {b"IHDR", b"PLTE", b"tRNS", b"IDAT", b"IEND", b"gAMA", b"sRGB", b"pHYs"}


def chunks(data: bytes):
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("not a PNG file")
    i = len(PNG_SIGNATURE)
    while i < len(data):
        (length,) = struct.unpack(">I", data[i:i + 4])
        kind = data[i + 4:i + 8]
        yield kind, data[i:i + 12 + length]
        i += 12 + length


def strip(data: bytes):
    """Return (clean_bytes, removed_chunk_names)."""
    out, removed = [PNG_SIGNATURE], []
    for kind, raw in chunks(data):
        if kind in KEEP:
            out.append(raw)
        else:
            removed.append(kind.decode("latin-1"))
    return b"".join(out), removed


def make_chunk(kind: bytes, payload: bytes) -> bytes:
    crc = zlib.crc32(kind + payload) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", crc)


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, "rb") as f:
        clean, removed = strip(f.read())
    with open(dst, "wb") as f:
        f.write(clean)
    print("removed:", ", ".join(removed) or "nothing")
