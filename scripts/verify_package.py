#!/usr/bin/env python3
"""
WeChat Sticker Package Verifier
Checks that a sticker output directory meets WeChat Sticker Store specifications.
"""

import os
import sys
from PIL import Image

PASS = "✓"
FAIL = "✗"
WARN = "!"

SPECS = {
    "main_sticker": {"size": (240, 240), "mode": "RGBA"},
    "thumbnail": {"size": (120, 120), "mode": "RGBA"},
    "cover": {"size": (240, 240), "mode": "RGBA"},
    "panel_icon": {"size": (50, 50), "mode": "RGBA"},
    "banner": {"size": (750, 400)},
    "appreciation_guide": {"size": (750, 560)},
    "appreciation_thanks": {"size": (120, 120)},
}


def check_image(path: str, expected_size: tuple, require_alpha: bool = False) -> tuple[bool, str]:
    """Check image dimensions and optionally transparency. Returns (passed, message)."""
    if not os.path.exists(path):
        return False, f"File not found: {path}"

    try:
        img = Image.open(path)
        w, h = img.size

        if (w, h) != expected_size:
            return False, f"Size {w}×{h} ≠ expected {expected_size[0]}×{expected_size[1]}"

        if require_alpha and img.mode != "RGBA":
            return False, f"Not RGBA (got {img.mode}) — background may not be transparent"

        if require_alpha and img.mode == "RGBA":
            import numpy as np
            alpha = np.array(img)[:, :, 3]
            if alpha.min() == 255:
                return False, "All pixels fully opaque — background may not have been removed"

        file_size_kb = os.path.getsize(path) / 1024
        return True, f"{w}×{h} {img.mode} ({file_size_kb:.0f} KB)"
    except Exception as e:
        return False, f"Cannot open image: {e}"


def count_stickers(directory: str, prefix: str) -> int:
    if not os.path.isdir(directory):
        return 0
    return sum(1 for f in os.listdir(directory) if f.startswith(prefix) and f.endswith(".png"))


def verify(output_dir: str, sticker_count: int = 0) -> bool:
    print(f"\n{'=' * 55}")
    print(f"  WeChat Sticker Package Verification")
    print(f"  Directory: {output_dir}")
    print(f"{'=' * 55}\n")

    all_passed = True

    # Auto-detect sticker count if not specified
    main_dir = os.path.join(output_dir, "main")
    thumb_dir = os.path.join(output_dir, "thumbnail")
    detected_main = count_stickers(main_dir, "sticker_")
    detected_thumb = count_stickers(thumb_dir, "thumb_")

    if sticker_count == 0:
        sticker_count = detected_main

    print(f"[Sticker Count]")
    if sticker_count in (16, 24):
        print(f"  {PASS} {sticker_count} stickers detected (valid: 16 or 24)")
    else:
        print(f"  {FAIL} {sticker_count} stickers detected (must be 16 or 24)")
        all_passed = False

    if detected_main != detected_thumb:
        print(f"  {WARN} Main ({detected_main}) and thumbnail ({detected_thumb}) counts differ")

    print()

    # Check all main stickers
    print("[Main Stickers — 240×240 RGBA]")
    for i in range(1, sticker_count + 1):
        path = os.path.join(main_dir, f"sticker_{i:02d}.png")
        passed, msg = check_image(path, (240, 240), require_alpha=True)
        icon = PASS if passed else FAIL
        print(f"  {icon} sticker_{i:02d}.png: {msg}")
        if not passed:
            all_passed = False

    print()

    # Check thumbnails
    print("[Thumbnails — 120×120 RGBA]")
    for i in range(1, sticker_count + 1):
        path = os.path.join(thumb_dir, f"thumb_{i:02d}.png")
        passed, msg = check_image(path, (120, 120), require_alpha=True)
        icon = PASS if passed else FAIL
        print(f"  {icon} thumb_{i:02d}.png: {msg}")
        if not passed:
            all_passed = False

    print()

    # Check single assets
    single_assets = [
        ("cover.png", (240, 240), True),
        ("panel_icon.png", (50, 50), True),
        ("banner.png", (750, 400), False),
        ("appreciation_guide.png", (750, 560), False),
        ("appreciation_thanks.png", (120, 120), False),
    ]

    print("[Single Assets]")
    for filename, size, require_alpha in single_assets:
        path = os.path.join(output_dir, filename)
        label = f"{filename} — {size[0]}×{size[1]}"
        if require_alpha:
            label += " RGBA"
        passed, msg = check_image(path, size, require_alpha=require_alpha)
        icon = PASS if passed else FAIL
        print(f"  {icon} {label}: {msg}")
        if not passed:
            all_passed = False

    # Check appreciation text
    print()
    print("[Appreciation Text]")
    text_path = os.path.join(output_dir, "appreciation_text.txt")
    if os.path.exists(text_path):
        with open(text_path, "r", encoding="utf-8") as f:
            text = f.read().strip()
        char_count = len(text)
        if 5 <= char_count <= 15:
            print(f"  {PASS} appreciation_text.txt: \"{text}\" ({char_count} 字)")
        else:
            print(f"  {WARN} appreciation_text.txt: \"{text}\" ({char_count} 字，建议 5-15 字)")
    else:
        print(f"  {WARN} appreciation_text.txt not found (optional but recommended)")

    print()
    print("=" * 55)
    if all_passed:
        print(f"  {PASS} ALL CHECKS PASSED — Package ready for submission!")
    else:
        print(f"  {FAIL} SOME CHECKS FAILED — Please fix before submitting.")
    print("=" * 55)
    print()

    return all_passed


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Verify a WeChat sticker output package against official specs."
    )
    parser.add_argument("output_dir", help="Path to the sticker output directory")
    parser.add_argument(
        "--count",
        type=int,
        default=0,
        help="Expected sticker count (16 or 24). Auto-detected if not specified.",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.output_dir):
        print(f"[error] Directory not found: {args.output_dir}")
        sys.exit(1)

    passed = verify(args.output_dir, args.count)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
