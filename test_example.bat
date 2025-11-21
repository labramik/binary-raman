@echo off
REM Quick test script for Raman Analysis Toolkit (Windows)

echo ==========================================
echo Raman Analysis Toolkit - Quick Test
echo ==========================================
echo.

REM Check if we're in the right directory
if not exist "scripts\detect_spectral_changes.py" (
    echo Error: Please run this script from the raman-analysis-toolkit directory
    echo Usage: test_example.bat
    exit /b 1
)

echo Testing with example DEA data...
echo.

cd scripts

REM Run the analysis
python detect_spectral_changes.py ^
    --txt ..\example_data\DEA_203K.txt ^
          ..\example_data\DEA_248K.txt ^
          ..\example_data\DEA_252K.txt ^
          ..\example_data\DEA_253K.txt ^
    --markers ..\example_data\DEA_markers.txt ^
    --prominence 0.005 ^
    --height 0.003 ^
    --plot ..\example_output.png

cd ..

echo.
echo ==========================================
echo Test complete!
echo.
echo Generated files:
echo   - spectral_changes_report.txt (in scripts\)
echo   - example_output.png (in main directory)
echo ==========================================
pause
