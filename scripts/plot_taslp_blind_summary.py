from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main() -> None:
    blind_rows = load_json("runs/paper_tables_taslp/stage_c/real_blind_aecmos.json")
    nlms_blind_path = ROOT / "runs" / "taslp_v31" / "nlms_eval" / "blind" / "nlms" / "aecmos_onnx_local" / "aggregate.json"
    if nlms_blind_path.exists() and not any(row.get("system") == "nlms" for row in blind_rows):
        row = json.loads(nlms_blind_path.read_text(encoding="utf-8"))
        blind_rows.append(
            {
                "system": "nlms",
                "mean_aecmos_echo": row.get("mean_aecmos_echo"),
                "mean_aecmos_other": row.get("mean_aecmos_other"),
                "num_examples": row.get("num_scored_rows", row.get("num_examples")),
            }
        )
    retention = load_json("runs/baseline_h16k_retrain/astws_h16k_blind_eval/blind_retention/summary.json")
    out_dir = ROOT / "paper" / "common" / "generated" / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    preferred_systems = ["ours", "astws_h16k", "nlms", "astws", "deep_echo"]
    labels = {
        "ours": "SC-AEC-Echo",
        "astws_h16k": "ASTWS-H16k",
        "nlms": "NLMS",
        "astws": "ASTWS transfer",
        "deep_echo": "Deep Echo transfer",
    }
    colors = {
        "ours": "#1f4e79",
        "astws_h16k": "#6f5b3e",
        "nlms": "#6a4c93",
        "astws": "#9f3b2d",
        "deep_echo": "#5a7d2b",
    }
    blind_map = {row["system"]: row for row in blind_rows if row["system"] in preferred_systems}
    retention_map = retention["systems"]
    systems = [system for system in preferred_systems if system in blind_map and system in retention_map]

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.5), constrained_layout=True)

    ax = axes[0]
    for system in systems:
        row = blind_map[system]
        x = row["mean_aecmos_other"]
        y = row["mean_aecmos_echo"]
        ax.scatter(x, y, s=135, color=colors[system], zorder=3)
        dx = -0.17 if system == "astws" else 0.02
        dy = 0.03 if system == "ours" else 0.02
        ax.text(x + dx, y + dy, labels[system], fontsize=9)
    x_values = [blind_map[system]["mean_aecmos_other"] for system in systems]
    y_values = [blind_map[system]["mean_aecmos_echo"] for system in systems]
    ax.set_xlim(min(x_values) - 0.15, max(x_values) + 0.15)
    ax.set_ylim(min(y_values) - 0.15, max(y_values) + 0.15)
    ax.set_xlabel("AECMOS-Other")
    ax.set_ylabel("AECMOS-Echo")
    ax.set_title("(a) Blind AECMOS operating point")
    ax.grid(alpha=0.25)

    ax = axes[1]
    x = np.arange(len(systems))
    width = 0.35
    below_01 = [retention_map[system]["mean_fraction_active_frames_below_0p1"] for system in systems]
    below_001 = [retention_map[system]["mean_fraction_active_frames_below_0p01"] for system in systems]
    ax.bar(x - width / 2, below_01, width=width, color=[colors[system] for system in systems], alpha=0.92, label="Active frames <0.1")
    ax.bar(x + width / 2, below_001, width=width, color=[colors[system] for system in systems], alpha=0.42, label="Active frames <0.01")
    ax.set_xticks(x)
    ax.set_xticklabels([labels[system] for system in systems], rotation=20, ha="right")
    ax.set_ylim(0.0, 0.65)
    ax.set_ylabel("Fraction of active frames")
    ax.set_title("(b) Active-frame dropout diagnostic")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, loc="upper right")

    png_path = out_dir / "taslp_blind_summary.png"
    pdf_path = out_dir / "taslp_blind_summary.pdf"
    fig.savefig(png_path, dpi=220)
    fig.savefig(pdf_path)
    plt.close(fig)


if __name__ == "__main__":
    main()
