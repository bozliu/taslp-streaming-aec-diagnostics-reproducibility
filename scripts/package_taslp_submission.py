from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path
import subprocess


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def rewrite_main_tex(text: str) -> str:
    replacements = {
        "../common/generated/taslp_clean_main_table.tex": "generated/taslp_clean_main_table.tex",
        "../common/generated/taslp_noisy_main_table.tex": "generated/taslp_noisy_main_table.tex",
        "../common/generated/taslp_low_ser_main_table.tex": "generated/taslp_low_ser_main_table.tex",
        "../common/generated/taslp_ablation_table.tex": "generated/taslp_ablation_table.tex",
        "../common/generated/taslp_gate_b_cue_attribution_table.tex": "generated/taslp_gate_b_cue_attribution_table.tex",
        "../common/generated/taslp_astws_h16k_recipe_table.tex": "generated/taslp_astws_h16k_recipe_table.tex",
        "../common/generated/taslp_scaec_recipe_table.tex": "generated/taslp_scaec_recipe_table.tex",
        "../common/generated/taslp_fidelity_table.tex": "generated/taslp_fidelity_table.tex",
        "../common/generated/taslp_blind_aecmos_table.tex": "generated/taslp_blind_aecmos_table.tex",
        "../common/generated/taslp_blind_retention_table.tex": "generated/taslp_blind_retention_table.tex",
        "../common/generated/taslp_returned_human_table.tex": "generated/taslp_returned_human_table.tex",
        "../common/generated/taslp_returned_human_scenario_table.tex": "generated/taslp_returned_human_scenario_table.tex",
        "../common/generated/taslp_aecmos_control_table.tex": "generated/taslp_aecmos_control_table.tex",
        "../common/generated/taslp_aecmos_validation_note.tex": "generated/taslp_aecmos_validation_note.tex",
        "../common/generated/taslp_historical_anchor_table.tex": "generated/taslp_historical_anchor_table.tex",
        "../common/generated/taslp_stats_appendix_table.tex": "generated/taslp_stats_appendix_table.tex",
        "../common/generated/taslp_historical_anchor_appendix_inline.tex": "generated/taslp_historical_anchor_appendix_inline.tex",
        "../common/generated/taslp_fidelity_appendix_inline.tex": "generated/taslp_fidelity_appendix_inline.tex",
        "../common/generated/taslp_baseline_audit_appendix_inline.tex": "generated/taslp_baseline_audit_appendix_inline.tex",
        "../common/generated/taslp_blind_retention_appendix_inline.tex": "generated/taslp_blind_retention_appendix_inline.tex",
        "../common/generated/taslp_synthetic_aecmos_appendix_inline.tex": "generated/taslp_synthetic_aecmos_appendix_inline.tex",
        "../common/generated/taslp_farend_protect_heldout_table.tex": "generated/taslp_farend_protect_heldout_table.tex",
        "../common/generated/figures/taslp_architecture_overview.pdf": "figures/architecture_overview.pdf",
        "../common/generated/figures/taslp_blind_summary.pdf": "figures/taslp_blind_summary.pdf",
        "../common/refs": "refs",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def resolve_ieeetran_bst() -> Path:
    result = subprocess.run(["kpsewhich", "IEEEtran.bst"], check=True, capture_output=True, text=True)
    path = Path(result.stdout.strip())
    if not path.exists():
        raise FileNotFoundError("Could not resolve IEEEtran.bst via kpsewhich")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a clean self-contained TASLP submission package and zip.")
    parser.add_argument("--output-dir", default="paper/exports/taslp_submission_ready_v32")
    parser.add_argument("--zip-path", default="paper/exports/taslp_submission_ready_v32.zip")
    args = parser.parse_args()

    output_dir = PROJECT_ROOT / args.output_dir
    zip_path = PROJECT_ROOT / args.zip_path

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    main_src = PROJECT_ROOT / "paper/taslp/main.tex"
    main_text = rewrite_main_tex(main_src.read_text(encoding="utf-8"))
    (output_dir / "main.tex").write_text(main_text, encoding="utf-8")

    files_to_copy = {
        PROJECT_ROOT / "paper/taslp/main.pdf": output_dir / "main.pdf",
        PROJECT_ROOT / "paper/taslp/IEEEtran.cls": output_dir / "IEEEtran.cls",
        resolve_ieeetran_bst(): output_dir / "IEEEtran.bst",
        PROJECT_ROOT / "paper/common/refs.bib": output_dir / "refs.bib",
        PROJECT_ROOT / "paper/taslp/main.bbl": output_dir / "main.bbl",
        PROJECT_ROOT / "paper/common/generated/taslp_clean_main_table.tex": output_dir / "generated/taslp_clean_main_table.tex",
        PROJECT_ROOT / "paper/common/generated/taslp_noisy_main_table.tex": output_dir / "generated/taslp_noisy_main_table.tex",
        PROJECT_ROOT / "paper/common/generated/taslp_low_ser_main_table.tex": output_dir / "generated/taslp_low_ser_main_table.tex",
        PROJECT_ROOT / "paper/common/generated/taslp_ablation_table.tex": output_dir / "generated/taslp_ablation_table.tex",
        PROJECT_ROOT / "paper/common/generated/taslp_gate_b_cue_attribution_table.tex": output_dir / "generated/taslp_gate_b_cue_attribution_table.tex",
        PROJECT_ROOT / "paper/common/generated/taslp_astws_h16k_recipe_table.tex": output_dir / "generated/taslp_astws_h16k_recipe_table.tex",
        PROJECT_ROOT / "paper/common/generated/taslp_scaec_recipe_table.tex": output_dir / "generated/taslp_scaec_recipe_table.tex",
        PROJECT_ROOT / "paper/common/generated/taslp_fidelity_table.tex": output_dir / "generated/taslp_fidelity_table.tex",
        PROJECT_ROOT / "paper/common/generated/taslp_blind_aecmos_table.tex": output_dir / "generated/taslp_blind_aecmos_table.tex",
        PROJECT_ROOT / "paper/common/generated/taslp_blind_retention_table.tex": output_dir / "generated/taslp_blind_retention_table.tex",
        PROJECT_ROOT / "paper/common/generated/taslp_returned_human_table.tex": output_dir / "generated/taslp_returned_human_table.tex",
        PROJECT_ROOT / "paper/common/generated/taslp_returned_human_scenario_table.tex": output_dir / "generated/taslp_returned_human_scenario_table.tex",
        PROJECT_ROOT / "paper/common/generated/taslp_aecmos_control_table.tex": output_dir / "generated/taslp_aecmos_control_table.tex",
        PROJECT_ROOT / "paper/common/generated/taslp_aecmos_validation_note.tex": output_dir / "generated/taslp_aecmos_validation_note.tex",
        PROJECT_ROOT / "paper/common/generated/taslp_historical_anchor_table.tex": output_dir / "generated/taslp_historical_anchor_table.tex",
        PROJECT_ROOT / "paper/common/generated/taslp_stats_appendix_table.tex": output_dir / "generated/taslp_stats_appendix_table.tex",
        PROJECT_ROOT / "paper/common/generated/taslp_historical_anchor_appendix_inline.tex": output_dir / "generated/taslp_historical_anchor_appendix_inline.tex",
        PROJECT_ROOT / "paper/common/generated/taslp_fidelity_appendix_inline.tex": output_dir / "generated/taslp_fidelity_appendix_inline.tex",
        PROJECT_ROOT / "paper/common/generated/taslp_baseline_audit_appendix_inline.tex": output_dir / "generated/taslp_baseline_audit_appendix_inline.tex",
        PROJECT_ROOT / "paper/common/generated/taslp_blind_retention_appendix_inline.tex": output_dir / "generated/taslp_blind_retention_appendix_inline.tex",
        PROJECT_ROOT / "paper/common/generated/taslp_synthetic_aecmos_appendix_inline.tex": output_dir / "generated/taslp_synthetic_aecmos_appendix_inline.tex",
        PROJECT_ROOT / "paper/common/generated/taslp_farend_protect_heldout_table.tex": output_dir / "generated/taslp_farend_protect_heldout_table.tex",
        PROJECT_ROOT / "paper/common/generated/figures/taslp_blind_summary.pdf": output_dir / "figures/taslp_blind_summary.pdf",
        PROJECT_ROOT / "paper/common/generated/figures/taslp_architecture_overview.pdf": output_dir / "figures/architecture_overview.pdf",
        PROJECT_ROOT / "paper/common/generated/figures/taslp_blind_summary.png": output_dir / "figures/taslp_blind_summary.png",
    }
    for src, dst in files_to_copy.items():
        copy_file(src, dst)

    zip_path.parent.mkdir(parents=True, exist_ok=True)
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(output_dir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(output_dir))

    print(zip_path.relative_to(PROJECT_ROOT))


if __name__ == "__main__":
    main()
