#!/usr/bin/env python3
"""
Calculate the literal color replacements needed when changing $jet.

Reads JET_OLD and JET_NEW from the environment and prints tab-separated
rows: label<TAB>old_value<TAB>new_value
"""

from __future__ import annotations

import colorsys
import os
import sys


def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb_tuple: tuple[int, int, int]) -> str:
    return "#%02x%02x%02x" % rgb_tuple


def to_hls(hex_str: str) -> tuple[float, float, float]:
    r, g, b = hex_to_rgb(hex_str)
    return colorsys.rgb_to_hls(r / 255, g / 255, b / 255)


def from_hls(h: float, l: float, s: float) -> str:
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return rgb_to_hex(tuple(round(v * 255) for v in (r, g, b)))


def lighten(hex_str: str, amount: float) -> str:
    h, l, s = to_hls(hex_str)
    return from_hls(h, min(1, l + amount), s)


def darken(hex_str: str, amount: float) -> str:
    h, l, s = to_hls(hex_str)
    return from_hls(h, max(0, l - amount), s)


def desaturate_to_gray(hex_str: str) -> str:
    h, l, _ = to_hls(hex_str)
    return from_hls(h, l, 0)


def transparentize(hex_str: str, amount: float) -> str:
    r, g, b = hex_to_rgb(hex_str)
    alpha = max(0, 1 - amount)
    alpha_str = f"{alpha:.3f}".rstrip("0").rstrip(".")
    return f"rgba({r}, {g}, {b}, {alpha_str})"


def entry(name: str, old_hex: str, new_hex: str) -> str:
    return f"{name}\t{old_hex}\t{new_hex}"


def main() -> int:
    try:
        jet_old = os.environ["JET_OLD"]
        jet_new = os.environ["JET_NEW"]
    except KeyError as exc:
        sys.stderr.write(f"Missing environment variable: {exc}\n")
        return 1

    rows: list[str] = []
    rows.append(entry("jet", jet_old, jet_new))

    rows.append(entry("lighten_2", lighten(jet_old, 0.02), lighten(jet_new, 0.02)))
    rows.append(entry("lighten_4", lighten(jet_old, 0.04), lighten(jet_new, 0.04)))
    rows.append(entry("lighten_6", lighten(jet_old, 0.06), lighten(jet_new, 0.06)))
    rows.append(entry("lighten_8", lighten(jet_old, 0.08), lighten(jet_new, 0.08)))
    rows.append(entry("darken_2", darken(jet_old, 0.02), darken(jet_new, 0.02)))

    # Borders: lighten(desaturate(lighten($jet, 4%), 100%), 14%)
    gray_old = desaturate_to_gray(lighten(jet_old, 0.04))
    gray_new = desaturate_to_gray(lighten(jet_new, 0.04))
    rows.append(entry("borders_gray", lighten(gray_old, 0.14), lighten(gray_new, 0.14)))

    # OSD background: transparentize(lighten($jet, 2%), 0.025)
    rows.append(
        entry(
            "osd_rgba",
            transparentize(lighten(jet_old, 0.02), 0.025),
            transparentize(lighten(jet_new, 0.02), 0.025),
        )
    )

    sys.stdout.write("\n".join(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
