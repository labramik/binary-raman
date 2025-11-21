---
name: raman-analysis
description: Generate scientific paragraphs analyzing solid-liquid phase transitions from temperature-dependent Raman spectroscopy data. Supports automated analysis from txt spectral files (PREFERRED) or manual analysis from annotated figures. Use when the user provides Raman spectra at multiple temperatures and asks to analyze phase transitions, create a report paragraph, or document spectral changes for binary mixtures or pure compounds. Automatically detects appearing/disappearing bands, intensity changes, and assigns phases.
---

# Raman Spectroscopy Phase Transition Analysis

## Overview

This skill generates publication-ready scientific paragraphs that analyze solid-liquid (S-L) phase transitions from temperature-dependent Raman spectroscopy data. 

**Two analysis modes:**

1. **Automated Analysis (RECOMMENDED)**: Uses `detect_spectral_changes.py` with txt spectral data files to objectively detect peaks, track appearances/disappearances, quantify intensity changes, and assign phases. This method eliminates visual inspection errors and detects subtle features invisible in images.

2. **Manual Analysis**: Analyzes annotated spectroscopy figures through visual inspection and manual extraction of band positions and temperatures.

All outputs follow the style of International Journal of Thermophysics reports.


## Workflow

### Recommended Workflow (with TXT files)

1. **Run automated detection** - Use `detect_spectral_changes.py` to objectively identify all spectral changes
2. **Review detection report** - Examine detected peaks, appearances, disappearances, and intensity changes
3. **Match with marker bands** - Assign detected changes to solid/liquid phase markers
4. **Generate scientific paragraph** - Create chronological analysis based on detected changes

### Alternative Workflow (with image only)

1. **Extract figure annotations** - Identify band positions (cm⁻¹) and temperatures (K) marked in the uploaded figure
2. **Visual inspection** - Trace bands across temperatures to identify changes
3. **Match with marker bands** - Compare extracted bands against provided compound marker bands
4. **Identify phase transitions** - Determine when solid/liquid phases appear or disappear
5. **Generate scientific paragraph** - Create a chronological analysis of spectral changes

## Input Requirements

### Preferred Workflow: TXT Files + Automated Detection

**RECOMMENDED**: Use spectral txt files with the `detect_spectral_changes.py` script for automatic, objective detection of spectral changes.

**Advantages of txt files:**
- Exact wavenumber and intensity values (no digitization errors)
- Automated peak detection and comparison
- Quantitative intensity measurements
- Detection of subtle features invisible in images
- Objective, reproducible analysis

**TXT file format:**
- Two columns: wavenumber (cm⁻¹), intensity
- Space, tab, or comma separated
- Temperature in filename (e.g., `DEA_248.15K.txt`) or provided separately
- One file per temperature

### Alternative Workflow: Annotated Figure

1. **Uploaded Figure**: An annotated Raman spectrum showing:
   - Multiple temperature-dependent spectra
   - Text labels marking band positions (e.g., "604", "1281 cm⁻¹")
   - Temperature labels for each spectrum (e.g., "254.15 K", "RT")
   - Visual markers (arrows, vertical lines, dotted lines) highlighting important bands

2. **Mixture Composition**: Molar fraction composition (e.g., "xDPA = 0.30" or "pure DMA")

3. **Marker Bands**: Reference bands for each compound and phase

### Marker Bands Format

Provide marker bands in ONE of these formats:

**Option A - Text file format** (`references/marker_bands.txt`):
```
COMPOUND1: DMA
  solid_I: 69, 113, 162, 221, 337, 489, 695, 880, 1045, 1095, 1155, 1173, 1194, 1428, 1451, 1735, 1745, 2744, 2766, 2815, 2845, 2867, 2899, 2911, 2930, 2943, 2958, 3016, 3028
  liquid: 280, 368, 434, 609, 646, 830, 849, 884, 1002, 1066, 1084, 1157, 1183, 1305, 1446, 1733, 2847, 2874, 2929, 2953, 3027

COMPOUND2: DPA
  solid_I: 74, 168, 532, 585, 701, 798, 862, 892, 918, 928, 989, 1032, 1041, 1050, 1089, 1119, 1140, 1248, 1292, 1302, 1311, 1424, 1453, 1723, 2738, 2792, 2831, 2876, 2893, 2920, 2934, 2973
  liquid: 250, 305, 344, 605, 764, 828, 874, 895, 923, 1041, 1061, 1082, 1132, 1294, 1424, 1452, 1731, 2739, 2881, 2937
```

For polymorphic compounds, add additional solid phases:
```
COMPOUND1: Example
  solid_I: [bands]
  solid_II: [bands]
  liquid: [bands]
```

**Option B - Dictionary format** (provided directly in prompt):
```python
compound1 = {
    "name": "DMA",
    "solid_I": [69, 113, 162, 221, 337, ...],
    "liquid": [280, 368, 434, 609, ...]
}

compound2 = {
    "name": "DPA",
    "solid_I": [74, 168, 532, 585, ...],
    "liquid": [250, 305, 344, 605, ...]
}
```

## Analysis Process

### Step 0: Automated Detection (when TXT files available)

**If spectral txt files are provided, ALWAYS start here:**

1. Run `detect_spectral_changes.py` with the provided txt files
2. Review the automated detection report
3. Use the objective peak detection data to inform the analysis
4. Proceed to Step 2 for phase assignment and narrative construction

This eliminates subjective visual inspection errors and detects subtle changes that may be invisible in image analysis.

### Step 1: Extract Figure Information and Visual Inspection

**If uncertain about any annotation**, ask the user for clarification rather than guessing.

Use the `extract_annotations.py` script or carefully examine the figure to identify:
- All band position labels (numbers in cm⁻¹)
- Temperature labels for each spectrum
- Which bands are highlighted (arrows, lines, dotted boxes)
- Room temperature (RT) spectrum location

**CRITICAL: Visual Spectral Inspection for Dashed Line Markers**

Vertical dashed lines indicate band changes across temperatures, NOT just band positions. For each dashed line marker:

1. **Visually trace the band across all temperatures** at that wavenumber position
2. **Determine the type of change occurring:**
   - **Appearance**: Band absent at lower temperatures, appears at higher temperatures
   - **Disappearance**: Band present at lower temperatures, disappears at higher temperatures
   - **Intensity increase**: Band grows stronger with increasing temperature
   - **Intensity decrease**: Band weakens with increasing temperature
   - **Shift**: Band position moves with temperature
   - **Splitting/merging**: Band transforms into multiple bands or multiple bands merge

3. **Identify the specific temperature(s)** where the change occurs or begins

4. **Note the baseline condition**: Is the band present or absent at the lowest temperature shown?

**Example interpretations:**
- Dashed line at 605 cm⁻¹: If no peak is visible at 248.15 K but a strong peak appears at 252.15 K → "liquid phase band appears at 605 cm⁻¹"
- Dashed line at 919 cm⁻¹: If a weak band at 248.15 K grows significantly stronger at 252.15 K → "band at 919 cm⁻¹ intensifies"
- Dashed line at 1462 cm⁻¹: If a strong band at 248.15 K disappears by 252.15 K → "solid phase band at 1462 cm⁻¹ disappears"

### Step 2: Identify Phase Assignments

Match extracted bands against the marker bands to determine:
- Which compound each band belongs to
- Whether the band indicates solid or liquid phase
- Special features (shoulders indicated by "sh.", triplets, broadening)

### Step 3: Construct the Narrative

Build the analysis chronologically by temperature, describing the **observed visual changes** from spectral inspection:

**At lowest temperature:**
- Dominant compound features
- Presence of minor compound contributions (if binary mixture)
- Key marker bands visible and their intensities

**During phase transition:**
- **Appearance of new bands**: Specify which bands appear and at what temperature (e.g., "liquid phase bands appear at 605, 644, and 790 cm⁻¹")
- **Disappearance of bands**: Note which solid phase bands diminish or vanish (e.g., "solid phase band at 1462 cm⁻¹ disappears")
- **Intensity changes**: Describe bands that grow or weaken (e.g., "band at 919 cm⁻¹ intensifies", "solid phase features gradually diminish")
- **Band transformations**: Note broadening, shoulders, shifts, or splitting
- **Coexistence**: Mention simultaneous presence of solid and liquid phase markers
- **Temperature specificity**: Always state at which temperature each change occurs

**At completion:**
- Temperature where transition completes
- Final spectrum equivalence to room temperature
- Interpretation (eutectic behavior, sequential melting, well-defined melting, etc.)

### Step 4: Generate the Paragraph

Write in scientific style following these guidelines:

**Required elements:**
- Start with temperature range and composition (e.g., "For the binary mixture with molar fraction x_DPA = 0.30...")
- Use precise wavenumbers for all band positions
- **Describe what happens to each marked band**: Don't just list positions - specify if bands appear, disappear, grow, or weaken (e.g., "liquid phase bands appear at 605, 644, and 790 cm⁻¹" not just "bands at 605, 644, 790")
- Include all temperatures where changes occur
- Mention specific bands that appear/disappear with action verbs
- Note spectral features (shoulders, triplets, broadening)
- Conclude with phase transition completion temperature

**Style conventions:**
- Use comparative language: "closely resembles", "equivalent to", "very similar to"
- Specify band characteristics: "subtle", "strong", "broad", "shoulder"
- **Use action verbs for band changes**: "appear", "disappear", "emerge", "vanish", "grow", "diminish", "intensify", "weaken", "persist", "transform"
- Use scientific terminology: "marker bands", "spectral features", "S-L transition"
- Include uncertainty indicators: "subtle", "noteworthy", "first indications"
- Use proper subscript formatting in markdown: x_DPA, cm⁻¹

**What to avoid:**
- Overly brief descriptions
- Missing specific band positions
- Omitting intermediate temperature observations
- Speculation beyond what the spectra show

## Output Format

Generate a single, well-structured paragraph formatted in markdown with proper subscripts. The paragraph should be publication-ready and follow the style of the example reference material.

Example structure:
```markdown
For the binary mixture with molar fraction x_DPA = 0.30, the spectrum recorded between 203.15 and 252.15 K closely resembles that of pure DMA, exhibiting some minor band shifts and a new shoulder at 206 cm⁻¹. [Continue with temperature-progressive analysis...] Finally, at 275.15 K, the spectrum of the mixture is equivalent to that obtained at room temperature, indicating the completion of the S-L phase transition.
```

## Resources

### scripts/detect_spectral_changes.py (RECOMMENDED)

**Primary tool for objective spectral analysis using txt data files.**

Automatically detects and quantifies:
- New peaks appearing at specific temperatures
- Peaks disappearing 
- Intensity changes (growth/diminishing) with percentage changes
- Peak position shifts
- **Shoulder peaks** (weak features adjacent to main peaks)
- **Weak peaks** (subtle features often missed visually)
- Assigns changes to solid/liquid phases using marker bands

**Key Features:**
- **Adjustable sensitivity**: Control prominence and height thresholds to detect weak features
- **Shoulder detection**: Automatically identifies and marks shoulders with (sh.) notation
- **Visual distinction**: Main peaks shown as red circles ●, shoulders as orange triangles ▲
- **Quantitative analysis**: Measures exact intensity changes and peak shifts

**Usage:**
```bash
# Basic analysis with default sensitivity
python detect_spectral_changes.py --txt spectrum_203K.txt spectrum_248K.txt spectrum_252K.txt spectrum_253K.txt

# High sensitivity (detect weak peaks and shoulders) - RECOMMENDED
python detect_spectral_changes.py --txt *.txt --markers marker_bands.txt --prominence 0.005 --height 0.003 --plot output.png

# Medium sensitivity (balanced)
python detect_spectral_changes.py --txt *.txt --prominence 0.01 --height 0.005

# Lower sensitivity (only strong peaks)
python detect_spectral_changes.py --txt *.txt --prominence 0.02 --height 0.01

# Disable shoulder detection (faster)
python detect_spectral_changes.py --txt *.txt --no-shoulders

# Adjust peak matching tolerance
python detect_spectral_changes.py --txt *.txt --tolerance 8.0
```

**Parameters:**
- `--prominence`: Minimum peak prominence (0.005 = high sensitivity, 0.02 = low sensitivity)
- `--height`: Minimum peak height relative to max intensity (0.003-0.01)
- `--tolerance`: Wavenumber tolerance for peak matching across temperatures (default: 5.0 cm⁻¹)
- `--no-shoulders`: Disable shoulder detection
- `--markers`: File with reference marker bands for phase assignment
- `--plot`: Output filename for visualization plot

**Output:**
- Comprehensive text report listing all detected changes
- Shoulders marked with "(sh.)" notation in reports
- Optional visualization plot with peaks (●) and shoulders (▲) distinguished
- Temperature-specific change assignments with phase labels

**When to use:** ALWAYS use this script when txt spectral data is available. It provides objective, quantitative analysis that eliminates visual estimation errors and detects subtle features invisible in manual inspection.

### scripts/extract_annotations.py

Python script for extracting band positions and temperatures from annotated Raman figures using OCR. Can be used when figure annotations are difficult to read manually and txt files are not available.

### references/example_outputs.md

Contains example analyses from published work showing the expected style, structure, and level of detail for the generated paragraphs.
