from __future__ import annotations

import hashlib
import re
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SHA256 = {
    "paper/taslp_submission_ready_v32.zip": "239ee4e6926d20a5e6f83a4fa2e69b134d1d68b8f0924d5d01d40d8a7d2f155e",
    "paper/taslp_submission_ready_v32/main.pdf": "5e375eb264dc7bfb246741f627564a50f62bd31acf7206a14a6d246d6e28a9f0",
}

FORBIDDEN_SUFFIXES = {
    ".wav",
    ".flac",
    ".mp3",
    ".m4a",
    ".ogg",
    ".pt",
    ".pth",
    ".ckpt",
    ".onnx",
    ".tflite",
}

SECRET_PATTERNS = [
    re.compile(r"gh[opsu]_[A-Za-z0-9_]{20,}"),
    re.compile(r"hf_[A-Za-z0-9]{20,}"),
    re.compile(r"vcp_[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]

TEXT_SUFFIXES = {".cff", ".json", ".md", ".py", ".txt", ".toml", ".tex", ".bib"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_release_files() -> list[Path]:
    return sorted(path for path in ROOT.rglob("*") if path.is_file() and ".git" not in path.parts)


def main() -> int:
    errors: list[str] = []

    for rel_path, expected in EXPECTED_SHA256.items():
        path = ROOT / rel_path
        if not path.exists():
            errors.append(f"missing expected artifact: {rel_path}")
            continue
        actual = sha256(path)
        if actual != expected:
            errors.append(f"hash mismatch for {rel_path}: {actual} != {expected}")

    zip_path = ROOT / "paper" / "taslp_submission_ready_v32.zip"
    if zip_path.exists():
        with zipfile.ZipFile(zip_path, "r") as archive:
            bad = archive.testzip()
        if bad is not None:
            errors.append(f"zip integrity failure at member: {bad}")

    for path in iter_release_files():
        rel = path.relative_to(ROOT).as_posix()
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append(f"forbidden raw/checkpoint artifact included: {rel}")
        if path.suffix.lower() in TEXT_SUFFIXES:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    errors.append(f"secret-like token pattern found in {rel}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("release package validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
