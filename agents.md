# Agents Overview

| Agent Name | Purpose | Input | Output |
| --- | --- | --- | --- |
| Automated Detection Agent | Run `scripts/detect_spectral_changes.py` to find peaks, appearances/disappearances, and match marker bands for phase assignment. | TXT spectra with temperatures in filenames plus optional marker file. | Console summary, `spectral_changes_report.txt`, and optional plot showing detected peaks. |
| Figure Interpretation Agent | Extract band positions and temperatures from annotated Raman spectra when txt files are absent, then align with marker bands. | Annotated Raman spectrum images with temperature labels and marker band list. | Structured notes of band changes by temperature and a publication-style paragraph describing phase behavior. |
