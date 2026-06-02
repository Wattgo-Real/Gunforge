import struct
import zlib

import pygame


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _decode_png_rgba(path):
    with open(path, "rb") as f:
        data = f.read()

    if not data.startswith(PNG_SIGNATURE):
        raise pygame.error(f"{path} is not a PNG file")

    pos = len(PNG_SIGNATURE)
    width = height = channels = None
    idat = bytearray()

    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        pos += 4
        chunk_type = data[pos:pos + 4]
        pos += 4
        chunk_data = data[pos:pos + length]
        pos += length + 4

        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, _, _, interlace = struct.unpack(">IIBBBBB", chunk_data)
            if bit_depth != 8 or color_type not in (2, 6) or interlace != 0:
                raise pygame.error(f"Unsupported PNG format: {path}")
            channels = 4 if color_type == 6 else 3
        elif chunk_type == b"IDAT":
            idat.extend(chunk_data)
        elif chunk_type == b"IEND":
            break

    if width is None or height is None or channels is None:
        raise pygame.error(f"Invalid PNG file: {path}")

    raw = zlib.decompress(bytes(idat))
    stride = width * channels
    rows = []
    prev = bytearray(stride)
    idx = 0

    for _ in range(height):
        filter_type = raw[idx]
        idx += 1
        scanline = bytearray(raw[idx:idx + stride])
        idx += stride

        for i in range(stride):
            left = scanline[i - channels] if i >= channels else 0
            up = prev[i]
            up_left = prev[i - channels] if i >= channels else 0

            if filter_type == 0:
                value = scanline[i]
            elif filter_type == 1:
                value = (scanline[i] + left) & 0xff
            elif filter_type == 2:
                value = (scanline[i] + up) & 0xff
            elif filter_type == 3:
                value = (scanline[i] + ((left + up) // 2)) & 0xff
            elif filter_type == 4:
                p = left + up - up_left
                pa = abs(p - left)
                pb = abs(p - up)
                pc = abs(p - up_left)
                predictor = left if pa <= pb and pa <= pc else (up if pb <= pc else up_left)
                value = (scanline[i] + predictor) & 0xff
            else:
                raise pygame.error(f"Unsupported PNG filter: {path}")

            scanline[i] = value

        rows.append(scanline)
        prev = scanline

    rgba = bytearray(width * height * 4)
    out_idx = 0
    for row in rows:
        for x in range(width):
            src_idx = x * channels
            rgba[out_idx:out_idx + 3] = row[src_idx:src_idx + 3]
            rgba[out_idx + 3] = row[src_idx + 3] if channels == 4 else 255
            out_idx += 4

    return width, height, bytes(rgba)


def load_image_surface(path):
    try:
        surface = pygame.image.load(path)
    except (OSError, pygame.error):
        width, height, rgba = _decode_png_rgba(path)
        surface = pygame.image.frombuffer(rgba, (width, height), "RGBA").copy()

    try:
        return surface.convert_alpha()
    except pygame.error:
        return surface

