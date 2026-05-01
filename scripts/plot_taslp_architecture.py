from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np
from PIL import Image, ImageChops, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "paper" / "common" / "generated" / "figures"
USER_SELECTED_SOURCE = (
    ROOT / "paper" / "common" / "figure_ideation" / "generated" / "architecture_overview_user_selected.png"
)


def crop_white_margin(image: Image.Image, *, threshold: int = 7, padding: int = 10) -> Image.Image:
    rgb = image.convert("RGB")
    white = Image.new("RGB", rgb.size, (255, 255, 255))
    diff = ImageChops.difference(rgb, white).convert("L")
    mask = diff.point(lambda value: 255 if value > threshold else 0)
    bbox = mask.getbbox()
    if bbox is None:
        return rgb
    left, top, right, bottom = bbox
    left = max(0, left - padding)
    top = max(0, top - padding)
    right = min(rgb.width, right + padding)
    bottom = min(rgb.height, bottom + padding)
    cropped = rgb.crop((left, top, right, bottom))
    return ImageOps.expand(cropped, border=4, fill="white")


def write_user_selected_architecture(pdf_path: Path, png_path: Path) -> bool:
    if not USER_SELECTED_SOURCE.exists():
        return False
    image = Image.open(USER_SELECTED_SOURCE)
    cropped = crop_white_margin(image)
    cropped.save(png_path)
    cropped.save(pdf_path, "PDF", resolution=300.0)
    return True


def add_box(
    ax: plt.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    text: str,
    *,
    facecolor: str,
    edgecolor: str = "#30343b",
    fontsize: float = 8.6,
    weight: str = "normal",
) -> None:
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.014,rounding_size=0.045",
        linewidth=0.9,
        edgecolor=edgecolor,
        facecolor=facecolor,
    )
    ax.add_patch(patch)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        fontweight=weight,
        color="#17191f",
        linespacing=1.12,
    )


def add_arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    color: str = "#7b8794",
    linewidth: float = 1.0,
    linestyle: str = "-",
    mutation_scale: float = 9.0,
) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=mutation_scale,
            linewidth=linewidth,
            linestyle=linestyle,
            color=color,
            shrinkA=2,
            shrinkB=2,
        )
    )


def add_wave(ax: plt.Axes, center: tuple[float, float], width: float, height: float, *, seed: int) -> None:
    rng = np.random.default_rng(seed)
    x = np.linspace(-1.0, 1.0, 140)
    envelope = np.exp(-2.8 * x**2)
    carrier = (
        np.sin(18 * x + rng.uniform(-0.6, 0.6))
        + 0.35 * np.sin(43 * x + rng.uniform(-0.8, 0.8))
        + 0.18 * np.sin(71 * x)
    )
    y = center[1] + 0.5 * height * envelope * carrier / np.max(np.abs(carrier))
    xx = center[0] + 0.5 * width * x
    ax.plot(xx, y, color="#606873", linewidth=0.75)


def add_list_item(ax: plt.Axes, x: float, y: float, width: float, height: float, text: str) -> None:
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.01,rounding_size=0.03",
        linewidth=0.7,
        edgecolor="#8a97a6",
        facecolor="#f9fbff",
    )
    ax.add_patch(patch)
    ax.text(x + width / 2, y + height / 2, text, ha="center", va="center", fontsize=7.2, color="#17191f")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = OUT_DIR / "taslp_architecture_overview.pdf"
    png_path = OUT_DIR / "taslp_architecture_overview.png"

    used_user_selected = write_user_selected_architecture(pdf_path, png_path)
    if used_user_selected:
        manifest_path = OUT_DIR.parent / "taslp_figure_manifest.json"
        manifest = {
            "architecture_figure": {
                "path": "paper/common/generated/figures/taslp_architecture_overview.pdf",
                "preview_path": "paper/common/generated/figures/taslp_architecture_overview.png",
                "source_path": "paper/common/figure_ideation/generated/architecture_overview_user_selected.png",
                "role": "architecture overview",
                "canonical_submission_asset": True,
                "format_note": "User-selected architecture visual is wrapped as PDF for submission; PNG is a local preview/source asset.",
            },
            "blind_summary_figure": {
                "path": "paper/common/generated/figures/taslp_blind_summary.pdf",
                "preview_path": "paper/common/generated/figures/taslp_blind_summary.png",
                "role": "blind AECMOS and retention summary",
                "canonical_submission_asset": True,
            },
        }
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
        return

    fig, ax = plt.subplots(figsize=(11.2, 4.15))
    ax.set_xlim(0, 11.35)
    ax.set_ylim(0, 4.05)
    ax.axis("off")

    gray = "#f2f5f8"
    blue = "#e8f0fb"
    green = "#e8f4e8"
    orange = "#ffe7ca"
    yellow = "#fff1c4"
    purple = "#eadcf0"

    add_box(ax, (0.08, 2.75), 1.23, 0.83, "Far-end\nreference", facecolor=blue, fontsize=8.6, weight="bold")
    add_wave(ax, (0.70, 2.96), 0.78, 0.18, seed=4)
    add_box(ax, (0.08, 1.55), 1.23, 0.83, "Mic\nwaveform", facecolor=blue, fontsize=8.6, weight="bold")
    add_wave(ax, (0.70, 1.76), 0.78, 0.18, seed=7)

    add_box(ax, (1.75, 2.02), 1.00, 0.95, "Streaming\nSTFT", facecolor=blue, fontsize=9.1, weight="bold")
    add_arrow(ax, (1.31, 3.17), (1.75, 2.58), color="#1e5a9a", linewidth=1.1)
    add_arrow(ax, (1.31, 1.97), (1.75, 2.36), color="#1e5a9a", linewidth=1.1)

    add_box(ax, (3.00, 2.18), 2.42, 1.45, "", facecolor=green, edgecolor="#4a7b50", fontsize=8.4)
    ax.text(
        4.21,
        3.31,
        "Online support-statistics estimator",
        ha="center",
        va="center",
        fontsize=7.55,
        fontweight="bold",
        color="#17191f",
    )
    support_items = [
        "12-band complex support",
        "12-band uncertainty",
        "5-way local delay cue",
        "speech-to-echo risk",
    ]
    for index, label in enumerate(support_items):
        add_list_item(ax, 3.18, 3.02 - index * 0.29, 2.06, 0.22, label)
    add_arrow(ax, (2.75, 2.50), (3.00, 2.86), color="#1e5a9a", linewidth=1.1)

    add_box(ax, (6.66, 2.40), 0.86, 0.82, "Causal\nbackbone\n\nh_t in R^256", facecolor=gray, fontsize=7.5, weight="bold")
    add_arrow(ax, (5.42, 2.90), (6.66, 2.82), color="#1e5a9a", linewidth=1.2)

    add_box(ax, (8.25, 2.17), 1.10, 1.18, "", facecolor=orange, edgecolor="#b56b25", fontsize=8.6)
    ax.text(8.80, 3.17, "Output\nheads", ha="center", va="center", fontsize=7.7, fontweight="bold")
    for index, label in enumerate(["residual echo", "speech gain", "noise mask"]):
        add_list_item(ax, 8.39, 2.76 - index * 0.30, 0.82, 0.23, label)
    add_arrow(ax, (7.52, 2.82), (8.25, 2.82), color="#1e5a9a", linewidth=1.2)

    add_box(ax, (9.56, 2.40), 0.90, 0.76, "ISTFT /\noverlap-add\nsynthesis", facecolor=orange, fontsize=7.0, weight="bold")
    add_arrow(ax, (9.33, 2.82), (9.55, 2.82), color="#1e5a9a", linewidth=1.1)

    add_box(ax, (10.64, 2.48), 0.62, 0.62, "Enhanced\noutput", facecolor=blue, fontsize=6.0, weight="bold")
    add_wave(ax, (10.95, 2.57), 0.34, 0.09, seed=11)
    add_arrow(ax, (10.46, 2.82), (10.64, 2.82), color="#1e5a9a", linewidth=1.1)

    add_box(ax, (4.45, 0.92), 0.95, 0.78, "Support\nencoder", facecolor=purple, fontsize=8.2, weight="bold")
    ax.text(4.93, 0.73, "c_t in R^192", ha="center", va="center", fontsize=7.6)
    add_arrow(ax, (4.22, 2.18), (4.93, 1.70), color="#4a7b50", linewidth=1.1)
    add_arrow(ax, (2.25, 2.02), (4.45, 1.28), color="#4a7b50", linewidth=1.0)

    add_box(ax, (5.80, 1.62), 1.20, 0.58, "Backbone-side\nsupport injection", facecolor=blue, fontsize=6.8, weight="bold")
    add_arrow(ax, (5.40, 1.30), (5.80, 1.88), color="#6e3a8a", linewidth=1.1)
    add_arrow(ax, (6.40, 2.20), (6.88, 2.40), color="#1e5a9a", linewidth=1.1)

    add_box(ax, (7.25, 0.92), 1.52, 0.72, "Head-side\nsupport adapter\nadditive ReZero or FiLM", facecolor=yellow, edgecolor="#be7a20", fontsize=6.1, weight="bold")
    add_arrow(ax, (5.40, 1.30), (7.25, 1.28), color="#6e3a8a", linewidth=1.1)
    add_arrow(ax, (7.95, 1.64), (8.72, 2.22), color="#6e3a8a", linewidth=1.1)

    ax.text(
        0.08,
        0.22,
        "All paths are causal at 16 kHz: 20 ms analysis window, 10 ms update hop.",
        fontsize=7.6,
        color="#434b57",
    )

    fig.savefig(pdf_path, bbox_inches="tight", pad_inches=0.03)
    fig.savefig(png_path, dpi=320, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    manifest_path = OUT_DIR.parent / "taslp_figure_manifest.json"
    manifest = {
        "architecture_figure": {
            "path": "paper/common/generated/figures/taslp_architecture_overview.pdf",
            "preview_path": "paper/common/generated/figures/taslp_architecture_overview.png",
            "role": "architecture overview",
            "canonical_submission_asset": True,
            "format_note": "Vector PDF is the submission dependency; PNG is only a local preview.",
        },
        "blind_summary_figure": {
            "path": "paper/common/generated/figures/taslp_blind_summary.pdf",
            "preview_path": "paper/common/generated/figures/taslp_blind_summary.png",
            "role": "blind AECMOS and retention summary",
            "canonical_submission_asset": True,
        },
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
