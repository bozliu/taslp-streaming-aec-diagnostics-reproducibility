# Reproducibility Notes

This package freezes the evidence record used by the TASLP v32 submission.

## What Can Be Reproduced Directly

- Inspect the self-contained LaTeX submission bundle in `paper/taslp_submission_ready_v32/`.
- Verify primary artifacts against `SHA256SUMS.txt`.
- Inspect generated tables and figures under `artifacts/`.
- Inspect returned item-level listening-summary aggregates under `artifacts/listening_summaries/`.

## What Requires External Data

Full waveform-level AEC evaluation requires official third-party audio and any model checkpoints used by the corresponding systems. Those raw inputs are not mirrored here. The package therefore focuses on fixed derived artifacts, summaries, validation snapshots, and manuscript-source reproducibility.

## Suggested Environment

The manuscript package was validated with Python in the `dl` conda environment and IEEEtran LaTeX tooling. A minimal Python environment for the included scripts should provide:

```text
numpy
matplotlib
pillow
PyYAML
```

LaTeX validation requires `latexmk`, `pdftoppm`, and `pdfinfo` or `qpdf`.
