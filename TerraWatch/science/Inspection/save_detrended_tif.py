from pathlib import Path
import numpy as np
import rasterio

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FINAL_DIR = PROJECT_ROOT / "data" / "final"

RAW_VERT_TIF = FINAL_DIR / "addis_ababa_vertical_displacement_cm.tif"
CLEAN_VERT_TIF = FINAL_DIR / "addis_ababa_vertical_detrended.tif"

def remove_planar_ramp(arr):
    """Fits and subtracts a 2D linear plane to remove the diagonal atmospheric/orbital tilt."""
    rows, cols = arr.shape
    y_grid, x_grid = np.mgrid[0:rows, 0:cols]
    valid = ~np.isnan(arr)
    
    A = np.column_stack([x_grid[valid], y_grid[valid], np.ones(np.count_nonzero(valid))])
    coeffs, _, _, _ = np.linalg.lstsq(A, arr[valid], rcond=None)
    a, b, c = coeffs
    
    return arr - (a * x_grid + b * y_grid + c)


with rasterio.open(RAW_VERT_TIF) as src:
    raw_data = src.read(1)
    detrended_data = remove_planar_ramp(raw_data).astype("float32")
    profile = src.profile.copy()

with rasterio.open(CLEAN_VERT_TIF, "w", **profile) as dst:
    dst.write(detrended_data, 1)

print(f"Saved clean detrended GeoTIFF: {CLEAN_VERT_TIF}")
print(f"Min: {np.nanmin(detrended_data):.2f} cm | Max: {np.nanmax(detrended_data):.2f} cm")
