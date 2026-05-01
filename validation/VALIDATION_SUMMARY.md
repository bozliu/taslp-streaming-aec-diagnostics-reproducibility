# Validation Summary

This release freezes the TASLP v32 submission package validated on 2026-05-01.

## Primary Artifacts

```text
paper/taslp_submission_ready_v32.zip
SHA256: 239ee4e6926d20a5e6f83a4fa2e69b134d1d68b8f0924d5d01d40d8a7d2f155e

paper/taslp_submission_ready_v32/main.pdf
SHA256: 5e375eb264dc7bfb246741f627564a50f62bd31acf7206a14a6d246d6e28a9f0
Pages: 11
```

## Checks Performed Before Freezing

- The self-contained submission bundle was rebuilt from the manuscript source.
- The bundled PDF was compared against the source PDF on selected pages.
- The ZIP archive passed integrity testing.
- Figure 1 uses the PDF architecture asset rather than a PNG dependency.
- The submission-facing manuscript text was scanned for stale rejected framing terms.
- No raw audio, generated enhanced clips, model checkpoints, caches, or credentials are included in this public package.

## Scope of Reproducibility

The package supports inspection of the fixed manuscript bundle, generated tables and figures, and returned item-level listening-summary aggregates. Full waveform-level re-evaluation requires obtaining third-party challenge audio and public comparator checkpoints from their official sources.
