import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

# Allow importing the analysis script directly from scripts/
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import detect_spectral_changes as dsc  # noqa: E402


class LoadTxtSpectrumTests(unittest.TestCase):
    def test_extracts_temperature_from_filename_and_data(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            txt_path = Path(tmpdir) / "sample_248K.txt"
            txt_path.write_text("100 0.1\n101 0.2\n")

            spectrum = dsc.load_txt_spectrum(txt_path)

            self.assertAlmostEqual(spectrum.temperature, 248.0)
            np.testing.assert_array_equal(spectrum.wavenumber, np.array([100.0, 101.0]))
            np.testing.assert_array_equal(spectrum.intensity, np.array([0.1, 0.2]))


class MarkerBandParsingTests(unittest.TestCase):
    def test_parses_numbers_and_ranges_with_annotations(self):
        marker_text = """DEA:
  solid: [183, 285, 326, 1025-1029, 1300 (sh.)]
  liquid: [252, 374, 468–470]
"""
        result = dsc.parse_marker_bands(marker_text)

        self.assertEqual(result["solid"], [183.0, 285.0, 326.0, 1025.0, 1300.0])
        self.assertEqual(result["liquid"], [252.0, 374.0, 468.0])


class CompareSpectraTests(unittest.TestCase):
    def _make_spectrum(self, wavenumbers, intensities, peaks, temperature):
        spectrum = dsc.RamanSpectrum(
            np.array(wavenumbers, dtype=float),
            np.array(intensities, dtype=float),
            temperature,
        )
        spectrum.peaks = np.array(peaks, dtype=int)
        spectrum.is_shoulder = np.zeros(len(peaks), dtype=bool)
        spectrum.peak_properties = {
            "prominences": np.zeros(len(peaks)),
            "widths": np.ones(len(peaks)),
        }
        return spectrum

    def test_detects_categories_of_changes(self):
        spec_cold = self._make_spectrum(
            wavenumbers=[100, 200, 300, 400],
            intensities=[0.1, 1.0, 0.4, 0.8],
            peaks=[1, 3],
            temperature=100.0,
        )
        spec_mid = self._make_spectrum(
            wavenumbers=[100, 200, 300, 400],
            intensities=[0.1, 1.0, 0.6, 0.2],
            peaks=[1, 2],
            temperature=200.0,
        )
        spec_hot = self._make_spectrum(
            wavenumbers=[100, 203, 300, 400],
            intensities=[0.1, 0.7, 0.15, 0.05],
            peaks=[1, 2],
            temperature=300.0,
        )

        changes = dsc.compare_spectra([spec_mid, spec_hot, spec_cold], tolerance=5.0)

        self.assertEqual(len(changes["appearing"]), 1)
        self.assertAlmostEqual(changes["appearing"][0]["wavenumber"], 300.0)
        self.assertAlmostEqual(changes["appearing"][0]["to_temp"], 200.0)

        self.assertEqual(len(changes["disappearing"]), 1)
        self.assertAlmostEqual(changes["disappearing"][0]["wavenumber"], 400.0)
        self.assertAlmostEqual(changes["disappearing"][0]["to_temp"], 200.0)

        self.assertEqual(len(changes["diminishing"]), 1)
        diminishing = changes["diminishing"][0]
        self.assertAlmostEqual(diminishing["wavenumber"], 300.0)
        self.assertLess(diminishing["change_percent"], -30.0)
        self.assertAlmostEqual(diminishing["to_temp"], 300.0)

        self.assertEqual(len(changes["shifting"]), 1)
        shifting = changes["shifting"][0]
        self.assertAlmostEqual(shifting["from_wavenumber"], 200.0)
        self.assertAlmostEqual(shifting["to_wavenumber"], 203.0)
        self.assertAlmostEqual(shifting["shift"], 3.0)


if __name__ == "__main__":
    unittest.main()
