# Reproducibility Package for Metric Divergence and Anti-Gaming Diagnostics for Streaming Acoustic Echo Cancellation

This repository is the frozen reproducibility package for the TASLP manuscript:

**Metric Divergence and Anti-Gaming Diagnostics for Streaming Acoustic Echo Cancellation**

The package supports review and citation of the manuscript's fixed evidence record. It contains the self-contained v32 TASLP submission archive, generated manuscript tables and figures, returned item-level listening-summary artifacts, selected validation snapshots, and lightweight scripts used to package and validate the manuscript artifact.

## Contents

- `paper/taslp_submission_ready_v32.zip`: self-contained IEEEtran LaTeX source bundle and compiled manuscript PDF.
- `paper/taslp_submission_ready_v32/`: unpacked copy of the same submission bundle for inspection.
- `artifacts/generated_tables/`: generated LaTeX tables used by the manuscript.
- `artifacts/figures/`: generated PDF/PNG manuscript figures.
- `artifacts/listening_summaries/`: returned item-level listening-summary aggregates used as claim-boundary evidence.
- `scripts/`: lightweight packaging, plotting, and validation scripts.
- `validation/`: source-project status and validation snapshots from the frozen v32 package.
- `SHA256SUMS.txt`: checksums for all release files except the checksum file itself.

To validate the public release package itself:

```bash
python scripts/validate_release_package.py
```

## Data and Audio Availability

This package does not redistribute raw third-party challenge audio or proprietary data. Where official challenge audio cannot be redistributed directly, the manuscript and package provide fixed derived artifacts, aggregate summaries, generated tables, and reconstruction guidance rather than raw audio mirrors.

## Submission Use

For IEEE submission metadata, use the Zenodo DOI created from the GitHub release of this repository and the title:

```text
Reproducibility Package for Metric Divergence and Anti-Gaming Diagnostics for Streaming Acoustic Echo Cancellation
```

## Primary Artifact Hashes

```text
paper/taslp_submission_ready_v32.zip
239ee4e6926d20a5e6f83a4fa2e69b134d1d68b8f0924d5d01d40d8a7d2f155e

paper/taslp_submission_ready_v32/main.pdf
5e375eb264dc7bfb246741f627564a50f62bd31acf7206a14a6d246d6e28a9f0
```

## Citation

Please cite the archived Zenodo release DOI. The repository also includes `CITATION.cff` and `.zenodo.json` metadata.
