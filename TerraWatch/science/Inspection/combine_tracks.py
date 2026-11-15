from pathlib import Path
import numpy as np
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import reproject, Resampling

# Fixed: added  to point to TerraWatch root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FINAL_DIR = PROJECT_ROOT / "data" / "final"
FINAL_DIR.mkdir(parents=True, exist_ok=True)

# Full Addis Ababa Metropolitan Area in UTM Zone 37N (meters)
ADDIS_BBOX_UTM = (462000, 975000, 492000, 1008000)  # (min_x, min_y, max_x, max_y)

full_asc = PROCESSED_DIR / "full_ascending_los_cm.tif"
full_desc = PROCESSED_DIR / "full_descending_los_cm.tif"

vertical_out = FINAL_DIR / "addis_ababa_vertical_displacement_cm.tif"
east_west_out = FINAL_DIR / "addis_ababa_east_west_cm.tif"

# Average NISAR incidence angle (~38 degrees)
theta = np.deg2rad(38.0)

# 1. Clip Ascending to full Addis Ababa and normalize median
with rasterio.open(full_asc) as src_asc:
    win_asc = from_bounds(*ADDIS_BBOX_UTM, transform=src_asc.transform)
    # Round window to exact integer pixels and allow boundless clipping
    win_asc = win_asc.round_offsets().round_lengths()
    asc_data = src_asc.read(1, window=win_asc, boundless=True, fill_value=np.nan)
    asc_data = asc_data - np.nanmedian(asc_data)
    asc_transform = src_asc.window_transform(win_asc)
    asc_crs = src_asc.crs
    height, width = asc_data.shape
    profile = src_asc.profile.copy()
    profile.update({
        "height": int(height),
        "width": int(width),
        "transform": asc_transform,
        "dtype": "float32",
        "nodata": np.nan
    })

# 2. Align & reproject Descending onto the exact Addis Ababa Ascending grid
desc_aligned = np.empty_like(asc_data)
with rasterio.open(full_desc) as src_desc:
    reproject(
        source=rasterio.band(src_desc, 1),
        destination=desc_aligned,
        src_transform=src_desc.transform,
        src_crs=src_desc.crs,
        dst_transform=asc_transform,
        dst_crs=asc_crs,
        resampling=Resampling.bilinear,
        src_nodata=np.nan,
        dst_nodata=np.nan
    )
    desc_aligned = desc_aligned - np.nanmedian(desc_aligned)

# 3. Calculate True Vertical (Up/Down) and East-West Motion
vertical_cm = (asc_data + desc_aligned) / (2.0 * np.cos(theta))
east_west_cm = (desc_aligned - asc_data) / (2.0 * np.sin(theta))

with rasterio.open(vertical_out, "w", **profile) as dst:
    dst.write(vertical_cm.astype("float32"), 1)

with rasterio.open(east_west_out, "w", **profile) as dst:
    dst.write(east_west_cm.astype("float32"), 1)

valid_px = np.count_nonzero(~np.isnan(vertical_cm))
print(f"Saved city-wide vertical map: {vertical_out}")
print(f"Valid pixels: {valid_px:,} | Min: {np.nanmin(vertical_cm):.2f} cm | Max: {np.nanmax(vertical_cm):.2f} cm")
