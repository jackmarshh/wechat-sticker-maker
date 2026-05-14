#!/usr/bin/env python3
"""
WeChat Sticker Processor
Splits a sticker grid image into individual stickers with transparent backgrounds.
"""

import os
import sys
import argparse
import numpy as np
from PIL import Image, ImageOps


def remove_white_background(img: Image.Image, threshold: int = 245) -> Image.Image:
    """Replace near-white pixels with transparency."""
    img = img.convert("RGBA")
    data = np.array(img)
    r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]
    white_mask = (r > threshold) & (g > threshold) & (b > threshold)
    data[:, :, 3] = np.where(white_mask, 0, a)
    return Image.fromarray(data, "RGBA")


def smart_crop_sticker(cell: Image.Image, padding_ratio: float = 0.1):
    """Crop to content bounding box, add padding, center on square canvas."""
    gray = cell.convert("L")
    inverted = ImageOps.invert(gray)
    mask = inverted.point(lambda x: 255 if x > 15 else 0, mode="1")
    bbox = mask.getbbox()

    if not bbox:
        return None

    char_img = cell.crop(bbox)
    char_w, char_h = char_img.size
    max_dim = max(char_w, char_h)
    canvas_size = int(max_dim / (1.0 - padding_ratio * 2))

    canvas = Image.new("RGBA", (canvas_size, canvas_size), (255, 255, 255, 0))
    offset = ((canvas_size - char_w) // 2, (canvas_size - char_h) // 2)
    canvas.paste(char_img, offset, char_img)
    return canvas


def process_grid(
    input_path: str,
    output_dir: str,
    grid: tuple[int, int] = (4, 4),
    target_size: tuple[int, int] = (240, 240),
    threshold: int = 245,
    cell_margin: int = 8,
) -> int:
    """
    Split a grid image into individual stickers.
    Returns the number of stickers successfully processed.
    """
    rows, cols = grid
    os.makedirs(os.path.join(output_dir, "main"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "thumbnail"), exist_ok=True)

    img = Image.open(input_path).convert("RGBA")
    width, height = img.size
    cell_w = width // cols
    cell_h = height // rows

    count = 0
    for r in range(rows):
        for c in range(cols):
            left = c * cell_w + cell_margin
            top = r * cell_h + cell_margin
            right = (c + 1) * cell_w - cell_margin
            bottom = (r + 1) * cell_h - cell_margin

            cell = img.crop((left, top, right, bottom))
            processed = remove_white_background(cell, threshold)
            sticker = smart_crop_sticker(processed)

            if sticker is None:
                print(f"  [warn] Cell ({r},{c}) appears empty, skipping.")
                continue

            count += 1
            main_path = os.path.join(output_dir, "main", f"sticker_{count:02d}.png")
            thumb_path = os.path.join(output_dir, "thumbnail", f"thumb_{count:02d}.png")

            sticker.resize(target_size, Image.Resampling.LANCZOS).save(main_path)
            sticker.resize((120, 120), Image.Resampling.LANCZOS).save(thumb_path)

            if count == 1:
                sticker.resize(target_size, Image.Resampling.LANCZOS).save(
                    os.path.join(output_dir, "cover.png")
                )
                sticker.resize((50, 50), Image.Resampling.LANCZOS).save(
                    os.path.join(output_dir, "panel_icon.png")
                )

    return count


def parse_grid(grid_str: str) -> tuple[int, int]:
    """Parse grid string like '4x4' or '3x8' into (rows, cols)."""
    try:
        parts = grid_str.lower().split("x")
        if len(parts) != 2:
            raise ValueError
        rows, cols = int(parts[0]), int(parts[1])
        if rows * cols not in (16, 24):
            print(f"[warn] Grid {grid_str} gives {rows * cols} cells; WeChat requires 16 or 24.")
        return rows, cols
    except (ValueError, TypeError):
        print(f"[error] Invalid grid format '{grid_str}'. Use e.g. '4x4' or '3x8'.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Process a WeChat sticker grid image into individual stickers."
    )
    parser.add_argument("input", help="Path to the input grid image (PNG or JPG)")
    parser.add_argument("output_dir", help="Directory to save the processed stickers")
    parser.add_argument(
        "--grid",
        default="4x4",
        help="Grid layout as ROWSxCOLS. Use '4x4' for 16 stickers or '3x8' for 24. (default: 4x4)",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=245,
        help="White background removal threshold (0-255, default: 245). Lower = more aggressive.",
    )
    parser.add_argument(
        "--margin",
        type=int,
        default=8,
        help="Pixel margin to trim from each cell edge (default: 8).",
    )
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"[error] Input file not found: {args.input}")
        sys.exit(1)

    grid = parse_grid(args.grid)
    rows, cols = grid
    total_cells = rows * cols

    print(f"Processing: {args.input}")
    print(f"Grid: {rows}×{cols} = {total_cells} cells")
    print(f"Output: {args.output_dir}")

    count = process_grid(
        input_path=args.input,
        output_dir=args.output_dir,
        grid=grid,
        threshold=args.threshold,
        cell_margin=args.margin,
    )

    print(f"\n✓ Done: {count}/{total_cells} stickers processed")
    print(f"  main/       — {count} × 240×240px PNG")
    print(f"  thumbnail/  — {count} × 120×120px PNG")
    print(f"  cover.png   — 240×240px PNG (from sticker_01)")
    print(f"  panel_icon.png — 50×50px PNG (from sticker_01)")

    if count < total_cells:
        print(f"\n[warn] {total_cells - count} empty cells detected.")
        print("  Tip: Regenerate the grid image with more consistent spacing.")


if __name__ == "__main__":
    main()
