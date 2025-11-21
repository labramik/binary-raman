#!/usr/bin/env python3
"""
Detect spectral changes in temperature-dependent Raman spectroscopy data.

This script analyzes Raman spectra at different temperatures to automatically detect:
- New bands appearing
- Bands disappearing
- Intensity changes (growth/diminishing)
- Peak position shifts
- Band broadening/narrowing

Supports two input modes:
1. TXT files (PREFERRED): One txt file per temperature with wavenumber-intensity data
2. Image file (FALLBACK): Annotated spectrum image (requires digitization)

Usage:
    # Using txt files (preferred)
    python detect_spectral_changes.py --txt spectrum_203K.txt spectrum_248K.txt spectrum_252K.txt spectrum_253K.txt
    
    # Using image file
    python detect_spectral_changes.py --image /path/to/spectrum.png

Requirements:
    pip install numpy scipy pandas matplotlib --break-system-packages
"""

import sys
import argparse
from pathlib import Path
import numpy as np
from typing import List, Dict, Tuple, Optional

try:
    from scipy.signal import find_peaks, argrelextrema
    from scipy.ndimage import gaussian_filter1d
except ImportError:
    print("Error: scipy not available. Install with: pip install scipy --break-system-packages")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("Warning: pandas not available. Install with: pip install pandas --break-system-packages")
    pd = None

try:
    import matplotlib.pyplot as plt
except ImportError:
    print("Warning: matplotlib not available. Install with: pip install matplotlib --break-system-packages")
    plt = None


class RamanSpectrum:
    """Represents a single Raman spectrum at a given temperature."""
    
    def __init__(self, wavenumber: np.ndarray, intensity: np.ndarray, temperature: float):
        self.wavenumber = wavenumber
        self.intensity = intensity
        self.temperature = temperature
        self.peaks = None
        self.peak_properties = None
    
    def detect_peaks(self, prominence: float = 0.005, width: int = 2, 
                     height: float = 0.005, distance: int = 3, detect_shoulders: bool = True):
        """
        Detect peaks in the spectrum, including weak peaks and shoulders.
        
        Parameters:
        -----------
        prominence : float
            Minimum prominence of peaks (relative to max intensity). 
            Lower = more sensitive. Default: 0.005 (0.5%)
        width : int
            Minimum width of peaks in data points. Default: 2
        height : float
            Minimum height of peaks (relative to max intensity). 
            Lower = detect weaker peaks. Default: 0.005 (0.5%)
        distance : int
            Minimum distance between peaks in data points. Default: 3
        detect_shoulders : bool
            If True, attempt to detect shoulder peaks. Default: True
        """
        # Normalize intensity
        norm_intensity = self.intensity / np.max(self.intensity)
        
        # Smooth the spectrum slightly to reduce noise
        smoothed = gaussian_filter1d(norm_intensity, sigma=1.0)
        
        # Find peaks
        peaks, properties = find_peaks(
            smoothed,
            prominence=prominence,
            width=width,
            height=height,
            distance=distance
        )
        
        self.peaks = peaks
        self.peak_properties = properties
        
        # Detect shoulders if requested
        if detect_shoulders:
            shoulders = self._detect_shoulders(smoothed, peaks, properties)
            if len(shoulders) > 0:
                # Combine peaks and shoulders
                all_peaks = np.concatenate([peaks, shoulders])
                # Sort by position
                sort_idx = np.argsort(all_peaks)
                self.peaks = all_peaks[sort_idx]
                
                # Mark which are shoulders
                self.is_shoulder = np.zeros(len(self.peaks), dtype=bool)
                shoulder_mask = np.isin(self.peaks, shoulders)
                self.is_shoulder = shoulder_mask[sort_idx]
            else:
                self.is_shoulder = np.zeros(len(peaks), dtype=bool)
        else:
            self.is_shoulder = np.zeros(len(peaks), dtype=bool)
        
        # Get peak positions in wavenumbers
        peak_wavenumbers = self.wavenumber[self.peaks]
        peak_intensities = self.intensity[self.peaks]
        
        return peak_wavenumbers, peak_intensities
    
    def _detect_shoulders(self, smoothed: np.ndarray, peaks: np.ndarray, 
                         properties: dict, shoulder_ratio: float = 0.3) -> np.ndarray:
        """
        Detect shoulder peaks - small peaks adjacent to large peaks.
        
        A shoulder is detected when:
        1. There's a local maximum near a main peak
        2. Its intensity is 20-50% of the main peak
        3. It's on the flank of the main peak
        
        Parameters:
        -----------
        smoothed : np.ndarray
            Smoothed intensity data
        peaks : np.ndarray
            Already detected main peaks
        properties : dict
            Peak properties from find_peaks
        shoulder_ratio : float
            Maximum ratio of shoulder to main peak (default: 0.3 = 30%)
        
        Returns:
        --------
        np.ndarray : Indices of detected shoulders
        """
        from scipy.signal import argrelextrema
        
        # Find all local maxima (less strict than main peaks)
        local_maxima = argrelextrema(smoothed, np.greater, order=2)[0]
        
        shoulders = []
        
        for peak in peaks:
            peak_height = smoothed[peak]
            
            # Look for local maxima near this peak
            # Define "near" as within the peak's width
            if 'widths' in properties:
                # Get the width of this peak
                peak_idx = np.where(peaks == peak)[0][0]
                width = properties['widths'][peak_idx]
                search_range = int(width * 3)  # Search within 3x the peak width
            else:
                search_range = 20  # Default search range
            
            # Find local maxima in the search range
            nearby_maxima = local_maxima[
                (local_maxima > peak - search_range) & 
                (local_maxima < peak + search_range) &
                (local_maxima != peak)  # Exclude the main peak itself
            ]
            
            for candidate in nearby_maxima:
                candidate_height = smoothed[candidate]
                
                # Check if it's a shoulder (20-50% of main peak height)
                if 0.2 * peak_height < candidate_height < shoulder_ratio * peak_height:
                    # Make sure it's not already detected as a main peak
                    if candidate not in peaks and candidate not in shoulders:
                        shoulders.append(candidate)
        
        return np.array(shoulders, dtype=int)
    
    def get_peak_list(self) -> List[Dict]:
        """Return list of detected peaks with properties."""
        if self.peaks is None:
            self.detect_peaks()
        
        peak_list = []
        for i, peak_idx in enumerate(self.peaks):
            peak_info = {
                'wavenumber': self.wavenumber[peak_idx],
                'intensity': self.intensity[peak_idx],
                'relative_intensity': self.intensity[peak_idx] / np.max(self.intensity),
                'is_shoulder': self.is_shoulder[i] if hasattr(self, 'is_shoulder') else False
            }
            
            # Add prominence and width for main peaks
            if hasattr(self, 'peak_properties') and not peak_info['is_shoulder']:
                # Find the index in the original peak_properties
                # (shoulders are added after, so they won't be in properties)
                main_peak_idx = i - np.sum(self.is_shoulder[:i])
                if main_peak_idx < len(self.peak_properties['prominences']):
                    peak_info['prominence'] = self.peak_properties['prominences'][main_peak_idx]
                    peak_info['width'] = self.peak_properties['widths'][main_peak_idx]
            
            peak_list.append(peak_info)
        
        return peak_list


def load_txt_spectrum(filepath: Path, temperature: Optional[float] = None) -> RamanSpectrum:
    """
    Load a Raman spectrum from a txt file.
    
    Expected format:
    - Two columns: wavenumber, intensity
    - Space, tab, or comma separated
    - Optional header lines (will be skipped automatically)
    
    Temperature can be:
    - Provided as parameter
    - Extracted from filename (e.g., "spectrum_248.15K.txt" or "spectrum_248K.txt")
    """
    # Try to extract temperature from filename if not provided
    if temperature is None:
        import re
        filename = filepath.name
        # Look for patterns like "248.15K" or "248K"
        temp_match = re.search(r'(\d{2,3}(?:\.\d{1,2})?)\s*K', filename)
        if temp_match:
            temperature = float(temp_match.group(1))
        else:
            # Try just a number
            temp_match = re.search(r'(\d{3})', filename)
            if temp_match:
                temperature = float(temp_match.group(1))
            else:
                raise ValueError(f"Cannot extract temperature from filename: {filename}. Please provide temperature explicitly.")
    
    # Load data - try different delimiters
    try:
        data = np.loadtxt(filepath, delimiter=None)  # Auto-detect whitespace
    except:
        try:
            data = np.loadtxt(filepath, delimiter=',')
        except:
            try:
                data = np.loadtxt(filepath, delimiter='\t')
            except:
                raise ValueError(f"Cannot load data from {filepath}. Check file format.")
    
    if data.shape[1] != 2:
        raise ValueError(f"Expected 2 columns (wavenumber, intensity), got {data.shape[1]}")
    
    wavenumber = data[:, 0]
    intensity = data[:, 1]
    
    return RamanSpectrum(wavenumber, intensity, temperature)


def match_peak(target_wn: float, peak_list: List[Dict], tolerance: float = 5.0) -> Optional[Dict]:
    """
    Find a peak in peak_list that matches target wavenumber within tolerance.
    
    Returns the closest matching peak or None if no match found.
    """
    matches = [p for p in peak_list if abs(p['wavenumber'] - target_wn) <= tolerance]
    
    if not matches:
        return None
    
    # Return closest match
    return min(matches, key=lambda p: abs(p['wavenumber'] - target_wn))


def compare_spectra(spectra: List[RamanSpectrum], tolerance: float = 5.0) -> Dict:
    """
    Compare multiple spectra to detect changes across temperatures.
    
    Note: Assumes peaks have already been detected in all spectra.
    
    Returns a dictionary with detected changes categorized by type.
    """
    # Sort spectra by temperature
    spectra = sorted(spectra, key=lambda s: s.temperature)
    
    changes = {
        'appearing': [],  # New peaks appearing
        'disappearing': [],  # Peaks disappearing
        'growing': [],  # Peaks increasing in intensity
        'diminishing': [],  # Peaks decreasing in intensity
        'shifting': [],  # Peaks changing position
        'stable': []  # Peaks present throughout
    }
    
    # Track peaks across temperatures
    # Start with peaks from the first (coldest) spectrum
    initial_peaks = spectra[0].get_peak_list()
    
    for spectrum_idx in range(1, len(spectra)):
        prev_spectrum = spectra[spectrum_idx - 1]
        curr_spectrum = spectra[spectrum_idx]
        
        prev_peaks = prev_spectrum.get_peak_list()
        curr_peaks = curr_spectrum.get_peak_list()
        
        # Check for new peaks appearing
        for curr_peak in curr_peaks:
            match = match_peak(curr_peak['wavenumber'], prev_peaks, tolerance)
            if match is None:
                changes['appearing'].append({
                    'wavenumber': curr_peak['wavenumber'],
                    'temperature': curr_spectrum.temperature,
                    'intensity': curr_peak['relative_intensity'],
                    'from_temp': prev_spectrum.temperature,
                    'to_temp': curr_spectrum.temperature,
                    'is_shoulder': curr_peak.get('is_shoulder', False)
                })
        
        # Check for peaks disappearing
        for prev_peak in prev_peaks:
            match = match_peak(prev_peak['wavenumber'], curr_peaks, tolerance)
            if match is None:
                changes['disappearing'].append({
                    'wavenumber': prev_peak['wavenumber'],
                    'temperature': curr_spectrum.temperature,
                    'last_seen': prev_spectrum.temperature,
                    'from_temp': prev_spectrum.temperature,
                    'to_temp': curr_spectrum.temperature,
                    'is_shoulder': prev_peak.get('is_shoulder', False)
                })
        
        # Check for intensity changes and shifts in matching peaks
        for prev_peak in prev_peaks:
            match = match_peak(prev_peak['wavenumber'], curr_peaks, tolerance)
            if match is not None:
                # Calculate relative intensity change
                intensity_change = (match['relative_intensity'] - prev_peak['relative_intensity']) / prev_peak['relative_intensity']
                
                # Check for significant intensity changes (>30%)
                if intensity_change > 0.3:
                    changes['growing'].append({
                        'wavenumber': prev_peak['wavenumber'],
                        'from_temp': prev_spectrum.temperature,
                        'to_temp': curr_spectrum.temperature,
                        'change_percent': intensity_change * 100,
                        'prev_intensity': prev_peak['relative_intensity'],
                        'curr_intensity': match['relative_intensity'],
                        'is_shoulder': prev_peak.get('is_shoulder', False)
                    })
                elif intensity_change < -0.3:
                    changes['diminishing'].append({
                        'wavenumber': prev_peak['wavenumber'],
                        'from_temp': prev_spectrum.temperature,
                        'to_temp': curr_spectrum.temperature,
                        'change_percent': intensity_change * 100,
                        'prev_intensity': prev_peak['relative_intensity'],
                        'curr_intensity': match['relative_intensity'],
                        'is_shoulder': prev_peak.get('is_shoulder', False)
                    })
                
                # Check for position shifts (>2 cm⁻¹)
                position_shift = match['wavenumber'] - prev_peak['wavenumber']
                if abs(position_shift) > 2.0:
                    changes['shifting'].append({
                        'from_wavenumber': prev_peak['wavenumber'],
                        'to_wavenumber': match['wavenumber'],
                        'shift': position_shift,
                        'from_temp': prev_spectrum.temperature,
                        'to_temp': curr_spectrum.temperature
                    })
    
    return changes


def generate_report(spectra: List[RamanSpectrum], changes: Dict, 
                   marker_bands: Optional[Dict] = None) -> str:
    """
    Generate a text report of detected spectral changes.
    
    Parameters:
    -----------
    spectra : List[RamanSpectrum]
        List of analyzed spectra
    changes : Dict
        Dictionary of detected changes from compare_spectra()
    marker_bands : Dict, optional
        Reference marker bands for solid/liquid phases
        Format: {'solid': [list of wavenumbers], 'liquid': [list of wavenumbers]}
    """
    report = []
    report.append("=" * 80)
    report.append("RAMAN SPECTRAL CHANGES ANALYSIS REPORT")
    report.append("=" * 80)
    report.append("")
    
    # Summary of analyzed spectra
    report.append("ANALYZED SPECTRA:")
    for spectrum in sorted(spectra, key=lambda s: s.temperature):
        num_peaks = len(spectrum.peaks) if spectrum.peaks is not None else 0
        num_shoulders = np.sum(spectrum.is_shoulder) if hasattr(spectrum, 'is_shoulder') else 0
        num_main = num_peaks - num_shoulders
        
        if num_shoulders > 0:
            report.append(f"  {spectrum.temperature:.2f} K: {num_main} main peaks + {num_shoulders} shoulders = {num_peaks} total features")
        else:
            report.append(f"  {spectrum.temperature:.2f} K: {num_peaks} peaks detected")
    report.append("")
    
    # Helper function to format wavenumber with shoulder notation
    def format_peak(change):
        wn = change['wavenumber']
        is_shoulder = change.get('is_shoulder', False)
        if is_shoulder:
            return f"{wn:.0f} cm⁻¹ (sh.)"
        else:
            return f"{wn:.0f} cm⁻¹"
    
    # Appearing peaks
    if changes['appearing']:
        report.append("NEW PEAKS APPEARING:")
        for change in sorted(changes['appearing'], key=lambda x: (x['temperature'], x['wavenumber'])):
            formatted = format_peak(change)
            report.append(f"  At {change['to_temp']:.2f} K: Band appears at {formatted}")
            if marker_bands:
                phase = assign_phase(change['wavenumber'], marker_bands)
                if phase:
                    report.append(f"    → Assigned to {phase} phase")
        report.append("")
    
    # Disappearing peaks
    if changes['disappearing']:
        report.append("PEAKS DISAPPEARING:")
        for change in sorted(changes['disappearing'], key=lambda x: (x['temperature'], x['wavenumber'])):
            formatted = format_peak(change)
            report.append(f"  At {change['to_temp']:.2f} K: Band at {formatted} disappears")
            if marker_bands:
                phase = assign_phase(change['wavenumber'], marker_bands)
                if phase:
                    report.append(f"    → Was assigned to {phase} phase")
        report.append("")
    
    # Growing peaks
    if changes['growing']:
        report.append("PEAKS GROWING IN INTENSITY:")
        for change in sorted(changes['growing'], key=lambda x: (x['to_temp'], x['wavenumber'])):
            formatted = format_peak(change)
            report.append(f"  {change['from_temp']:.2f} → {change['to_temp']:.2f} K: "
                         f"Band at {formatted} grows by {change['change_percent']:.0f}%")
        report.append("")
    
    # Diminishing peaks
    if changes['diminishing']:
        report.append("PEAKS DIMINISHING IN INTENSITY:")
        for change in sorted(changes['diminishing'], key=lambda x: (x['to_temp'], x['wavenumber'])):
            formatted = format_peak(change)
            report.append(f"  {change['from_temp']:.2f} → {change['to_temp']:.2f} K: "
                         f"Band at {formatted} decreases by {change['change_percent']:.0f}%")
        report.append("")
    
    # Shifting peaks
    if changes['shifting']:
        report.append("PEAKS SHIFTING POSITION:")
        for change in sorted(changes['shifting'], key=lambda x: x['to_temp']):
            report.append(f"  {change['from_temp']:.2f} → {change['to_temp']:.2f} K: "
                         f"Band shifts from {change['from_wavenumber']:.0f} to "
                         f"{change['to_wavenumber']:.0f} cm⁻¹ "
                         f"(shift: {change['shift']:+.0f} cm⁻¹)")
        report.append("")
    
    report.append("=" * 80)
    
    return "\n".join(report)


def assign_phase(wavenumber: float, marker_bands: Dict, tolerance: float = 10.0) -> Optional[str]:
    """
    Assign a wavenumber to a phase based on marker bands.
    
    Parameters:
    -----------
    wavenumber : float
        Wavenumber to assign
    marker_bands : Dict
        Dictionary with 'solid', 'liquid', etc. keys containing lists of marker wavenumbers
    tolerance : float
        Maximum distance to consider a match
    """
    for phase, bands in marker_bands.items():
        for marker in bands:
            if abs(wavenumber - marker) <= tolerance:
                return phase
    return None


def plot_spectra_comparison(spectra: List[RamanSpectrum], changes: Dict, 
                           output_file: Optional[str] = None):
    """
    Create a visualization of the spectra with detected changes highlighted.
    Main peaks shown as circles, shoulders shown as triangles.
    """
    if plt is None:
        print("Warning: matplotlib not available. Skipping plot generation.")
        return
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Sort by temperature
    spectra = sorted(spectra, key=lambda s: s.temperature)
    
    # Plot spectra with offset
    offset = 0
    offset_step = 0.3
    
    for spectrum in spectra:
        # Normalize
        norm_intensity = spectrum.intensity / np.max(spectrum.intensity) + offset
        ax.plot(spectrum.wavenumber, norm_intensity, label=f'{spectrum.temperature:.2f} K', linewidth=1)
        
        # Mark peaks
        if spectrum.peaks is not None:
            peak_wn = spectrum.wavenumber[spectrum.peaks]
            peak_int = spectrum.intensity[spectrum.peaks] / np.max(spectrum.intensity) + offset
            
            # Separate main peaks and shoulders
            if hasattr(spectrum, 'is_shoulder'):
                main_peaks_mask = ~spectrum.is_shoulder
                shoulder_mask = spectrum.is_shoulder
                
                # Plot main peaks as circles
                ax.plot(peak_wn[main_peaks_mask], peak_int[main_peaks_mask], 
                       'o', markersize=4, alpha=0.7, color='red')
                
                # Plot shoulders as triangles
                if np.any(shoulder_mask):
                    ax.plot(peak_wn[shoulder_mask], peak_int[shoulder_mask], 
                           '^', markersize=4, alpha=0.7, color='orange')
            else:
                ax.plot(peak_wn, peak_int, 'ro', markersize=4, alpha=0.6)
        
        offset += offset_step
    
    ax.set_xlabel('Raman shift (cm⁻¹)', fontsize=12)
    ax.set_ylabel('Raman intensity (a.u.)', fontsize=12)
    ax.set_title('Temperature-Dependent Raman Spectra with Detected Peaks', fontsize=14)
    
    # Create custom legend
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], marker='o', color='w', markerfacecolor='red', 
                             markersize=6, alpha=0.7, label='Main peaks'),
                      Line2D([0], [0], marker='^', color='w', markerfacecolor='orange', 
                             markersize=6, alpha=0.7, label='Shoulders')]
    ax.legend(handles=legend_elements + [Line2D([0], [0], color=c, linewidth=1, 
              label=f'{s.temperature:.2f} K') for s, c in 
              zip(spectra, plt.cm.tab10.colors[:len(spectra)])], 
              loc='upper right', fontsize=9)
    
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"\nPlot saved to: {output_file}")
    else:
        plt.show()


def parse_marker_bands(marker_string: str) -> Dict:
    """
    Parse marker bands from a string format.
    
    Example format:
    DEA:
      solid: [183, 285, 326, ...]
      liquid: [252, 374, 468, ...]
    """
    import re
    
    marker_bands = {}
    
    # Find all phase definitions
    phase_pattern = r'(\w+):\s*\[([\d,\s\(\)\–\-\w\.]+)\]'
    matches = re.findall(phase_pattern, marker_string)
    
    for phase, bands_str in matches:
        # Extract numbers, handling ranges like "1025-1029" or "1300 (sh.)"
        numbers = []
        # Remove annotations like (sh.), (dublet), etc.
        bands_str = re.sub(r'\([^)]+\)', '', bands_str)
        # Handle ranges with – or -
        bands_str = re.sub(r'(\d+)\s*[–\-]\s*(\d+)', r'\1', bands_str)
        # Extract all numbers
        for num in re.findall(r'\d+', bands_str):
            numbers.append(float(num))
        
        marker_bands[phase] = numbers
    
    return marker_bands


def main():
    parser = argparse.ArgumentParser(
        description='Detect spectral changes in temperature-dependent Raman data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze txt files
  python detect_spectral_changes.py --txt spectrum_203K.txt spectrum_248K.txt spectrum_252K.txt
  
  # With marker bands
  python detect_spectral_changes.py --txt *.txt --markers markers.txt
  
  # Generate plot
  python detect_spectral_changes.py --txt *.txt --plot output.png
        """
    )
    
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--txt', nargs='+', help='TXT files containing spectra (one per temperature)')
    input_group.add_argument('--image', help='Image file with annotated spectra')
    
    parser.add_argument('--markers', help='File containing marker bands for phase assignment')
    parser.add_argument('--plot', help='Output file for comparison plot (e.g., output.png)')
    parser.add_argument('--tolerance', type=float, default=5.0, 
                       help='Wavenumber tolerance for peak matching (default: 5.0 cm⁻¹)')
    parser.add_argument('--prominence', type=float, default=0.005,
                       help='Minimum peak prominence for detection (default: 0.005, range: 0.001-0.05)')
    parser.add_argument('--height', type=float, default=0.005,
                       help='Minimum peak height for detection (default: 0.005)')
    parser.add_argument('--no-shoulders', action='store_true',
                       help='Disable shoulder detection (faster but less complete)')
    
    args = parser.parse_args()
    
    # Detect shoulders unless disabled
    detect_shoulders = not args.no_shoulders
    
    # Load spectra
    spectra = []
    
    if args.txt:
        print(f"Loading {len(args.txt)} spectrum files...\n")
        for txt_file in args.txt:
            try:
                spectrum = load_txt_spectrum(Path(txt_file))
                spectra.append(spectrum)
                print(f"  ✓ Loaded {txt_file}: {spectrum.temperature:.2f} K, "
                      f"{len(spectrum.wavenumber)} data points")
            except Exception as e:
                print(f"  ✗ Error loading {txt_file}: {e}")
                continue
    
    elif args.image:
        print("Error: Image digitization not yet implemented.")
        print("Please use txt files for now with --txt option.")
        sys.exit(1)
    
    if len(spectra) < 2:
        print("\nError: Need at least 2 spectra to compare changes.")
        sys.exit(1)
    
    print(f"\nSuccessfully loaded {len(spectra)} spectra\n")
    
    # Load marker bands if provided
    marker_bands = None
    if args.markers:
        try:
            with open(args.markers, 'r') as f:
                marker_string = f.read()
            marker_bands = parse_marker_bands(marker_string)
            print("Marker bands loaded:")
            for phase, bands in marker_bands.items():
                print(f"  {phase}: {len(bands)} bands")
            print()
        except Exception as e:
            print(f"Warning: Could not load marker bands: {e}\n")
    
    # Detect changes
    print("Analyzing spectral changes...")
    
    # Set peak detection parameters for all spectra
    for spectrum in spectra:
        spectrum.detect_peaks(
            prominence=args.prominence,
            height=args.height,
            detect_shoulders=detect_shoulders
        )
    
    changes = compare_spectra(spectra, tolerance=args.tolerance)
    
    # Generate report
    report = generate_report(spectra, changes, marker_bands)
    print("\n" + report)
    
    # Save report to file
    report_file = "spectral_changes_report.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"\nReport saved to: {report_file}")
    
    # Generate plot if requested
    if args.plot:
        plot_spectra_comparison(spectra, changes, args.plot)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
