from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], *, cwd: Path) -> None:
    subprocess.run(command, cwd=str(cwd), check=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def render_pages(pdf_path: Path, pages: list[int], output_dir: Path) -> dict[int, Path]:
    rendered: dict[int, Path] = {}
    for page in pages:
        prefix = output_dir / f"page{page}"
        run(
            [
                "pdftoppm",
                "-f",
                str(page),
                "-l",
                str(page),
                "-png",
                str(pdf_path),
                str(prefix),
            ],
            cwd=PROJECT_ROOT,
        )
        candidates = sorted(output_dir.glob(f"page{page}-*.png"))
        if not candidates:
            raise FileNotFoundError(f"Failed to render page {page} from {pdf_path}")
        rendered[page] = candidates[0]
    return rendered


def page_count(pdf_path: Path) -> int:
    try:
        result = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            cwd=str(PROJECT_ROOT),
            check=True,
            capture_output=True,
            text=True,
        )
        for line in result.stdout.splitlines():
            if line.startswith("Pages:"):
                return int(line.split(":", 1)[1].strip())
    except subprocess.CalledProcessError:
        pass

    fallback = subprocess.run(
        ["qpdf", "--show-npages", str(pdf_path)],
        cwd=str(PROJECT_ROOT),
        check=True,
        capture_output=True,
        text=True,
    )
    text = fallback.stdout.strip()
    if text.isdigit():
        return int(text)
    raise ValueError(f"Could not determine page count for {pdf_path}")


def refresh_zip_entries(zip_path: Path, replacements: dict[str, Path]) -> None:
    """Rewrite selected zip entries after export-side compilation.

    The package script copies the source PDF into the export directory and zips
    that clean file set. This validator then compiles the self-contained export
    directory to prove it builds independently. Refreshing only the validated PDF
    avoids a stale zip/folder byte mismatch without adding LaTeX aux files.
    """
    tmp_zip = zip_path.with_suffix(zip_path.suffix + ".tmp")
    replaced = set(replacements)
    with zipfile.ZipFile(zip_path, "r") as source, zipfile.ZipFile(
        tmp_zip, "w", compression=zipfile.ZIP_DEFLATED
    ) as target:
        for info in source.infolist():
            if info.filename in replaced:
                continue
            target.writestr(info, source.read(info.filename))
        for arcname, path in replacements.items():
            target.write(path, arcname)
    tmp_zip.replace(zip_path)


def ensure_architecture_figure_pdf() -> None:
    target = PROJECT_ROOT / "paper/common/generated/figures/taslp_architecture_overview.pdf"
    if target.exists():
        return
    source = PROJECT_ROOT / "paper/exports/taslp_submission_ready_v31/figures/architecture_overview.pdf"
    if source.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        return
    run(["conda", "run", "-n", "dl", "python", str(PROJECT_ROOT / "scripts" / "plot_taslp_architecture.py")], cwd=PROJECT_ROOT)


def ensure_submission_figure_dependencies(export_dir: Path, zip_path: Path) -> None:
    main_text = (export_dir / "main.tex").read_text(encoding="utf-8")
    if "figures/architecture_overview.png" in main_text:
        raise ValueError("Figure 1 must use figures/architecture_overview.pdf, not the PNG preview.")
    if (export_dir / "figures" / "architecture_overview.png").exists():
        raise ValueError("Submission export must not include architecture_overview.png as a Figure 1 dependency.")
    with zipfile.ZipFile(zip_path, "r") as archive:
        names = set(archive.namelist())
    if "figures/architecture_overview.png" in names:
        raise ValueError("Submission zip must not include architecture_overview.png as a Figure 1 dependency.")
    if "figures/architecture_overview.pdf" not in names:
        raise ValueError("Submission zip is missing figures/architecture_overview.pdf.")


def cleanup_latex_artifacts(directory: Path) -> None:
    """Remove build byproducts from a submission export directory after validation."""
    for suffix in (
        ".aux",
        ".blg",
        ".fdb_latexmk",
        ".fls",
        ".log",
        ".out",
        ".synctex.gz",
    ):
        for path in directory.glob(f"*{suffix}"):
            path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and validate TASLP source/export PDFs.")
    parser.add_argument("--pages", nargs="+", type=int, default=[3, 5, 8, 9])
    parser.add_argument("--export-dir", default="paper/exports/taslp_submission_ready")
    parser.add_argument("--zip-path", default="paper/exports/taslp_submission_ready.zip")
    args = parser.parse_args()

    source_dir = PROJECT_ROOT / "paper" / "taslp"
    export_dir = PROJECT_ROOT / args.export_dir

    run(["conda", "run", "-n", "dl", "python", str(PROJECT_ROOT / "scripts" / "generate_taslp_assets.py")], cwd=PROJECT_ROOT)
    ensure_architecture_figure_pdf()
    run(["conda", "run", "-n", "dl", "python", str(PROJECT_ROOT / "scripts" / "plot_taslp_blind_summary.py")], cwd=PROJECT_ROOT)
    run(["conda", "run", "-n", "dl", "latexmk", "-g", "-pdf", "-interaction=nonstopmode", "main.tex"], cwd=source_dir)
    run(
        [
            "conda",
            "run",
            "-n",
            "dl",
            "python",
            str(PROJECT_ROOT / "scripts" / "package_taslp_submission.py"),
            "--output-dir",
            args.export_dir,
            "--zip-path",
            args.zip_path,
        ],
        cwd=PROJECT_ROOT,
    )
    ensure_submission_figure_dependencies(export_dir, PROJECT_ROOT / args.zip_path)
    run(["conda", "run", "-n", "dl", "latexmk", "-g", "-pdf", "-interaction=nonstopmode", "main.tex"], cwd=export_dir)

    source_pdf = source_dir / "main.pdf"
    export_pdf = export_dir / "main.pdf"
    source_pages = page_count(source_pdf)
    export_pages = page_count(export_pdf)
    if source_pages != export_pages:
        raise ValueError(f"Page count mismatch: source={source_pages}, export={export_pages}")

    with tempfile.TemporaryDirectory(prefix="taslp-validate-") as tmp:
        tmp_dir = Path(tmp)
        source_render_dir = tmp_dir / "source"
        export_render_dir = tmp_dir / "export"
        source_render_dir.mkdir(parents=True, exist_ok=True)
        export_render_dir.mkdir(parents=True, exist_ok=True)

        source_rendered = render_pages(source_pdf, args.pages, source_render_dir)
        export_rendered = render_pages(export_pdf, args.pages, export_render_dir)

        page_digests: dict[int, dict[str, str]] = {}
        mismatches: list[int] = []
        for page in args.pages:
            source_hash = sha256(source_rendered[page])
            export_hash = sha256(export_rendered[page])
            page_digests[page] = {"source": source_hash, "export": export_hash}
            if source_hash != export_hash:
                mismatches.append(page)

        if mismatches:
            zip_refreshed = False
        else:
            refresh_zip_entries(PROJECT_ROOT / args.zip_path, {"main.pdf": export_pdf})
            zip_refreshed = True
            cleanup_latex_artifacts(export_dir)

        result = {
            "source_pdf": source_pdf.relative_to(PROJECT_ROOT).as_posix(),
            "export_pdf": export_pdf.relative_to(PROJECT_ROOT).as_posix(),
            "page_count": source_pages,
            "validated_pages": args.pages,
            "page_hashes": page_digests,
            "matched": not mismatches,
            "mismatched_pages": mismatches,
            "zip_refreshed": zip_refreshed,
        }
        print(json.dumps(result, ensure_ascii=True, indent=2))
        if mismatches:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
