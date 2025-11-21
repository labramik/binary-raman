# Raman Spectroscopy Phase Transition Analysis Toolkit

Complete toolkit for automated analysis of temperature-dependent Raman spectroscopy data to study solid-liquid phase transitions.

## Features

✨ **Automated Peak Detection** - Uses scipy algorithms to detect all peaks including weak features
🔍 **Shoulder Detection** - Automatically identifies shoulder peaks adjacent to main peaks
📊 **Quantitative Analysis** - Measures exact intensity changes and peak shifts
📈 **Phase Assignment** - Matches detected peaks to solid/liquid marker bands
📉 **Comprehensive Reports** - Generates detailed text reports and visualization plots
📝 **Publication-Ready Output** - Follows International Journal of Thermophysics style

## Installation

### Requirements
- Python 3.7 or higher
- Required packages: numpy, scipy, pandas, matplotlib

### Quick Install

```bash
# Install all dependencies
pip install -r requirements.txt
```

Or install packages individually:

```bash
pip install numpy scipy pandas matplotlib
```

## Quick Start

### 1. Prepare Your Data

**TXT files format:**
- Two columns: wavenumber (cm⁻¹), intensity
- Space, tab, or comma separated
- One file per temperature
- Include temperature in filename (e.g., `DEA_203K.txt`, `sample_248.15K.txt`)

**Example file (`DEA_203K.txt`):**
```
100.5  0.023
101.0  0.025
101.5  0.028
...
1800.0  0.145
```

**Marker bands file (`markers.txt`):**
```
DEA:
  solid: [183, 285, 326, ..., 1728, 1735]
  liquid: [252, 374, 468, ..., 1453, 1731]
```

See `references/marker_bands_example.txt` for complete format.

### 2. Run Analysis

**Basic usage:**
```bash
cd scripts
python detect_spectral_changes.py --txt ../data/DEA_203K.txt ../data/DEA_248K.txt ../data/DEA_252K.txt ../data/DEA_253K.txt
```

**With marker bands and plot (RECOMMENDED):**
```bash
python detect_spectral_changes.py --txt ../data/DEA_*.txt --markers ../markers.txt --plot ../output.png
```

**High sensitivity (detect all features including weak peaks):**
```bash
python detect_spectral_changes.py --txt ../data/*.txt --markers ../markers.txt --prominence 0.005 --height 0.003 --plot output.png
```

### 3. Review Output

The script generates:
1. **Console report** - Summary printed to terminal
2. **`spectral_changes_report.txt`** - Detailed text report with all changes
3. **Plot file** (if `--plot` specified) - Visualization with peaks marked

## Command-Line Options

```
--txt FILE [FILE ...]     Input txt files (required)
--markers FILE             Marker bands file for phase assignment
--plot FILE                Output plot filename (e.g., output.png)
--prominence FLOAT         Peak prominence threshold (default: 0.005)
                          Lower = more sensitive (0.001-0.05)
--height FLOAT            Peak height threshold (default: 0.005)
--tolerance FLOAT         Peak matching tolerance in cm⁻¹ (default: 5.0)
--no-shoulders            Disable shoulder detection
```

## Sensitivity Settings

| Use Case | Prominence | Height | Description |
|----------|-----------|--------|-------------|
| Maximum sensitivity | 0.005 | 0.003 | Detect all features including very weak peaks |
| Balanced (default) | 0.005 | 0.005 | Good for most analyses |
| Conservative | 0.01 | 0.01 | Only clear, strong peaks |
| Strong peaks only | 0.02 | 0.02 | Minimal detection |

## Example Output

```
================================================================================
RAMAN SPECTRAL CHANGES ANALYSIS REPORT
================================================================================

ANALYZED SPECTRA:
  203.00 K: 32 main peaks + 2 shoulders = 34 total features
  248.00 K: 28 peaks detected
  252.00 K: 24 peaks detected
  253.00 K: 18 peaks detected

NEW PEAKS APPEARING:
  At 252.00 K: Band appears at 603 cm⁻¹
    → Assigned to liquid phase
  At 252.00 K: Band appears at 919 cm⁻¹
    → Assigned to liquid phase

PEAKS DISAPPEARING:
  At 248.00 K: Band at 581 cm⁻¹ (sh.) disappears
    → Was assigned to solid phase
  At 253.00 K: Band at 1462 cm⁻¹ disappears
    → Was assigned to solid phase

PEAKS GROWING IN INTENSITY:
  203.00 → 248.00 K: Band at 581 cm⁻¹ (sh.) grows by 1079%
  203.00 → 248.00 K: Band at 801 cm⁻¹ (sh.) grows by 1321%
...
```

## File Structure

```
raman-analysis-toolkit/
├── scripts/
│   ├── detect_spectral_changes.py    # Main analysis script
│   └── extract_annotations.py        # OCR extraction (optional)
├── references/
│   ├── example_outputs.md            # Style examples
│   └── marker_bands_example.txt      # Example marker format
├── requirements.txt                  # Python dependencies
├── SKILL.md                          # Complete documentation
├── TXT_FILES_GUIDE.md               # Detailed usage guide
├── CHANGELOG.md                      # Version history
└── README.md                         # This file
```

## Documentation

- **`SKILL.md`** - Complete skill documentation with all workflows
- **`TXT_FILES_GUIDE.md`** - Step-by-step guide for txt file analysis
- **`CHANGELOG.md`** - Version history and updates
- **`references/example_outputs.md`** - Example analysis paragraphs with style guidelines

## Understanding the Output

### Peak Detection
- **Main peaks** (●): Strong, well-defined peaks shown as red circles in plots
- **Shoulders** (▲): Weaker features adjacent to main peaks, shown as orange triangles, marked with "(sh.)" in reports

### Changes Detected
- **Appearing**: New peaks detected at higher temperatures
- **Disappearing**: Peaks present at lower temperatures that vanish
- **Growing**: Peaks increasing in intensity (>30% change)
- **Diminishing**: Peaks decreasing in intensity (>30% change)
- **Shifting**: Peaks moving position (>2 cm⁻¹)

### Phase Assignment
When marker bands are provided, detected peaks are automatically assigned to phases:
- Solid phase (e.g., solid_I, solid_II)
- Liquid phase
- Unassigned (peaks not matching any marker)

## Advanced Usage

### Custom Shoulder Detection Sensitivity

Edit the script to adjust `shoulder_ratio` parameter in `_detect_shoulders()`:
```python
shoulders = self._detect_shoulders(smoothed, peaks, properties, shoulder_ratio=0.3)
```
- Lower values (0.2): Detect more shoulders
- Higher values (0.5): Only very prominent shoulders

### Batch Processing

Process multiple samples:
```bash
for sample in sample1 sample2 sample3; do
    python detect_spectral_changes.py \
        --txt ../data/${sample}_*.txt \
        --markers ../markers_${sample}.txt \
        --plot ${sample}_analysis.png
done
```

## Troubleshooting

**Problem:** Too many peaks detected (noise)
- **Solution:** Increase `--prominence` to 0.01 or 0.02

**Problem:** Missing weak peaks
- **Solution:** Decrease `--prominence` to 0.003 or use `--height 0.002`

**Problem:** Shoulders not detected
- **Solution:** Ensure shoulder detection is enabled (don't use `--no-shoulders`)

**Problem:** Peaks not matching between temperatures
- **Solution:** Increase `--tolerance` to 8.0 or 10.0 cm⁻¹

**Problem:** Temperature not extracted from filename
- **Solution:** Ensure filename contains temperature like "248K" or "248.15K"

## Citation

If you use this toolkit in your research, please acknowledge:
- Raman spectroscopy phase transition analysis following International Journal of Thermophysics methodology
- Peak detection using scipy.signal.find_peaks algorithms

## Support

For issues, questions, or suggestions:
1. Check the documentation in `SKILL.md` and `TXT_FILES_GUIDE.md`
2. Review example outputs in `references/example_outputs.md`
3. Consult the troubleshooting section above

## License

This toolkit is provided for academic and research use.

## Version

Version 2.0 (November 2025)
- Added automated txt file analysis
- Implemented shoulder detection
- Enhanced weak peak detection
- Improved visualization with peak/shoulder distinction
