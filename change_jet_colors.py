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


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb_tuple: tuple[int, int, int]) -> str:
    return "#%02x%02x%02x" % rgb_tuple


def to_hls(hex_str: str) -> tuple[float, float, float]:
    r, g, b = hex_to_rgb(hex_str)
    return colorsys.rgb_to_hls(r / 255, g / 255, b / 255)


def from_hls(h: float, l: float, s: float) -> str:
    r, g, b = colorsys.hls_to_rgb(h, clamp01(l), clamp01(s))
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


def mix(color1: str, color2: str, weight: float) -> str:
    """
    Approximate Sass mix(): weight is 0.0-1.0 applied to color1.
    """
    w = clamp01(weight)
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    r = round(r1 * w + r2 * (1 - w))
    g = round(g1 * w + g2 * (1 - w))
    b = round(b1 * w + b2 * (1 - w))
    return rgb_to_hex((r, g, b))


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

    # GTK derived backgrounds (dark variant): keep the blue-tinted chain consistent.
    base_color_old = lighten(jet_old, 0.06)
    base_color_new = lighten(jet_new, 0.06)
    bg_color_old = lighten(jet_old, 0.08)
    bg_color_new = lighten(jet_new, 0.08)
    menu_color_old = lighten(jet_old, 0.02)
    menu_color_new = lighten(jet_new, 0.02)
    borders_color_old = darken(bg_color_old, 0.10)
    borders_color_new = darken(bg_color_new, 0.10)
    rows.append(entry("gtk_base_color", base_color_old, base_color_new))
    rows.append(entry("gtk_bg_color", bg_color_old, bg_color_new))
    rows.append(entry("gtk_menu_color", menu_color_old, menu_color_new))
    rows.append(entry("gtk_borders_color", borders_color_old, borders_color_new))
    rows.append(entry("gtk_headerbar_bg_color", darken(bg_color_old, 0.03), darken(bg_color_new, 0.03)))
    rows.append(entry("gtk_menu_selected_color", lighten(bg_color_old, 0.06), lighten(bg_color_new, 0.06)))
    rows.append(
        entry(
            "gtk_scrollbar_bg_color",
            mix(base_color_old, bg_color_old, 0.5),
            mix(base_color_new, bg_color_new, 0.5),
        )
    )
    rows.append(
        entry(
            "gtk_sidebar_bg_color",
            mix(bg_color_old, base_color_old, 0.5),
            mix(bg_color_new, base_color_new, 0.5),
        )
    )
    rows.append(
        entry(
            "gtk_insensitive_bg_color",
            mix(bg_color_old, base_color_old, 0.6),
            mix(bg_color_new, base_color_new, 0.6),
        )
    )

    backdrop_base_color_old = lighten(base_color_old, 0.03)
    backdrop_base_color_new = lighten(base_color_new, 0.03)
    backdrop_bg_color_old = lighten(bg_color_old, 0.03)
    backdrop_bg_color_new = lighten(bg_color_new, 0.03)
    backdrop_borders_color_old = mix(borders_color_old, bg_color_old, 0.8)
    backdrop_borders_color_new = mix(borders_color_new, bg_color_new, 0.8)
    rows.append(entry("gtk_backdrop_base_color", backdrop_base_color_old, backdrop_base_color_new))
    rows.append(entry("gtk_backdrop_bg_color", backdrop_bg_color_old, backdrop_bg_color_new))
    rows.append(entry("gtk_backdrop_borders_color", backdrop_borders_color_old, backdrop_borders_color_new))
    rows.append(
        entry(
            "gtk_backdrop_dark_fill",
            mix(backdrop_borders_color_old, backdrop_bg_color_old, 0.35),
            mix(backdrop_borders_color_new, backdrop_bg_color_new, 0.35),
        )
    )
    rows.append(
        entry(
            "gtk_backdrop_insensitive_color",
            lighten(backdrop_bg_color_old, 0.15),
            lighten(backdrop_bg_color_new, 0.15),
        )
    )

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
