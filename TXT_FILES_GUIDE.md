# Using TXT Files for Raman Analysis - Quick Start Guide

## Why Use TXT Files?

TXT files provide **objective, quantitative analysis** with:
- ✓ Exact peak positions and intensities
- ✓ Automatic detection of subtle changes
- ✓ **Shoulder peak detection** - identifies weak features adjacent to main peaks
- ✓ **Weak peak detection** - finds subtle features invisible in images
- ✓ Quantitative intensity measurements
- ✓ No manual visual inspection errors
- ✓ Reproducible, scientific results

## File Preparation

### TXT File Format

Your spectral data files should have:
- **Two columns**: wavenumber (cm⁻¹), intensity
- **Separator**: space, tab, or comma
- **Temperature in filename**: e.g., `DEA_203.15K.txt` or `spectrum_248K.txt`
- **One file per temperature**

Example file content (`DEA_248.15K.txt`):
```
100.5  0.023
101.0  0.025
101.5  0.028
...
1800.0  0.145
```

### Marker Bands File

Create a marker bands file listing reference peaks for each phase:

```
DEA:
  solid: [183, 285, 326, ..., 1728, 1735]
  liquid: [252, 374, 468, ..., 1453, 1731]
```

See `references/marker_bands_example.txt` for a complete example.

## Usage

### Step 1: Install Requirements

```bash
pip install numpy scipy pandas matplotlib --break-system-packages
```

### Step 2: Run Detection

```bash
# Basic analysis
python scripts/detect_spectral_changes.py --txt DEA_203K.txt DEA_248K.txt DEA_252K.txt DEA_253K.txt

# With marker bands for phase assignment
python scripts/detect_spectral_changes.py --txt *.txt --markers marker_bands.txt

# Generate visualization plot
python scripts/detect_spectral_changes.py --txt *.txt --plot comparison.png --markers marker_bands.txt
```

### Step 3: Review Output

The script generates:
1. **Console report** showing:
   - Peaks appearing at each temperature
   - Peaks disappearing
   - Intensity changes (growing/diminishing)
   - Peak shifts
   - Phase assignments (if marker bands provided)

2. **Text file**: `spectral_changes_report.txt` with full details

3. **Plot** (if requested): Visualization with detected peaks marked

## Example Output

```
================================================================================
RAMAN SPECTRAL CHANGES ANALYSIS REPORT
================================================================================

ANALYZED SPECTRA:
  203.15 K: 45 peaks detected
  248.15 K: 42 peaks detected
  252.15 K: 38 peaks detected
  253.15 K: 35 peaks detected

NEW PEAKS APPEARING:
  At 252.15 K: Band appears at 605 cm⁻¹
    → Assigned to liquid phase
  At 252.15 K: Band appears at 644 cm⁻¹
    → Assigned to liquid phase
  At 252.15 K: Band appears at 882 cm⁻¹
    → Assigned to liquid phase

PEAKS DISAPPEARING:
  At 248.15 K: Band at 1462 cm⁻¹ disappears
    → Was assigned to solid phase

PEAKS GROWING IN INTENSITY:
  248.15 → 252.15 K: Band at 919 cm⁻¹ grows by 145%
...
```

## Adjusting Sensitivity

If detection is too sensitive or not sensitive enough:

```bash
# Less sensitive (only detect major peaks)
python scripts/detect_spectral_changes.py --txt *.txt --prominence 0.05

# More sensitive (detect subtle features)
python scripts/detect_spectral_changes.py --txt *.txt --prominence 0.01

# Wider tolerance for peak matching
python scripts/detect_spectral_changes.py --txt *.txt --tolerance 10.0
```

## Next Steps

After running automated detection:
1. Review the report to understand all spectral changes
2. Use the detected changes to write the scientific paragraph
3. Follow the style guidelines in `references/example_outputs.md`
4. Ensure all detected changes are incorporated chronologically

## Troubleshooting

**Problem**: "Cannot extract temperature from filename"
- **Solution**: Include temperature in filename (e.g., `spectrum_248K.txt`) or provide it explicitly

**Problem**: "Expected 2 columns, got X"
- **Solution**: Check that your file has only wavenumber and intensity columns

**Problem**: Too many/few peaks detected
- **Solution**: Adjust `--prominence` parameter (default: 0.02)

**Problem**: Peaks not matching between temperatures
- **Solution**: Adjust `--tolerance` parameter (default: 5.0 cm⁻¹)
