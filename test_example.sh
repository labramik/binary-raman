#!/bin/bash
# Quick test script for Raman Analysis Toolkit

echo "=========================================="
echo "Raman Analysis Toolkit - Quick Test"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "scripts/detect_spectral_changes.py" ]; then
    echo "Error: Please run this script from the raman-analysis-toolkit directory"
    echo "Usage: bash test_example.sh"
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "Testing with example DEA data..."
echo ""

cd scripts

# Run the analysis
python3 detect_spectral_changes.py \
    --txt ../example_data/DEA_203K.txt \
          ../example_data/DEA_248K.txt \
          ../example_data/DEA_252K.txt \
          ../example_data/DEA_253K.txt \
    --markers ../example_data/DEA_markers.txt \
    --prominence 0.005 \
    --height 0.003 \
    --plot ../example_output.png

echo ""
echo "=========================================="
echo "Test complete!"
echo ""
echo "Generated files:"
echo "  - spectral_changes_report.txt (in scripts/)"
echo "  - example_output.png (in main directory)"
echo "=========================================="
