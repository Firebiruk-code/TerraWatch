from pathlib import Path
import h5py
import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.windows import from_bounds

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "nisar"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Bounding box covering Addis Ababa & all AAU campuses (UTM Zone 37N meters)
# Covers roughly 38.70°E to 38.86°E and 8.95°N to 9.08°N (including 6 Kilo, 4 Kilo, 5 Kilo, and Kilinto)
AAU_BBOX_UTM = (467000, 989000, 485000, 1004000)  # (min_x, min_y, max_x, max_y)

def find_first_path(h5, target_name, filter_str=""):
    matches = []
    def visitor(path, obj):
        if isinstance(obj, h5py.Dataset) and path.split("/")[-1] == target_name:
            if filter_str in path:
                matches.append(path)
    h5.visititems(visitor)
    return sorted(matches)[0] if matches else None

def process_gunw_to_geotiff(h5_path, track_label):
    print(f"\nProcessing {track_label}: {h5_path.name}")
    
    with h5py.File(h5_path, "r") as h5:
        # 1. Prefer frequencyA (high resolution); fallback to any available frequency
        freq_filter = "frequencyA" if find_first_path(h5, "unwrappedPhase", "frequencyA") else ""
        
        phase_path = find_first_path(h5, "unwrappedPhase", freq_filter)
        coh_path = find_first_path(h5, "coherenceMagnitude", freq_filter)
        conn_path = find_first_path(h5, "connectedComponents", freq_filter)
        x_path = find_first_path(h5, "xCoordinates", freq_filter)
        y_path = find_first_path(h5, "yCoordinates", freq_filter)
        proj_path = find_first_path(h5, "projection", freq_filter)
        freq_val_path = find_first_path(h5, "centerFrequency", freq_filter)

        # 2. Read arrays & metadata
        phase = h5[phase_path][:]
        coherence = h5[coh_path][:]
        conn_comp = h5[conn_path][:] if conn_path else np.ones_like(phase)
        x = h5[x_path][:]
        y = h5[y_path][:]
        epsg = int(h5[proj_path][()])
        
        center_freq = float(np.asarray(h5[freq_val_path][()]).squeeze())
        wavelength_m = 299792458.0 / center_freq

        # 3. Mask noisy pixels (coherence < 0.3 or unwrapping island 0)
        valid_mask = (coherence >= 0.3) & (conn_comp > 0)
        clean_phase = np.where(valid_mask, phase, np.nan)

        # 4. Convert radians to Line-of-Sight (LOS) displacement in centimeters
        # Negative = ground moving away from satellite (subsidence)
        # Positive = ground moving toward satellite (uplift)
        los_cm = (clean_phase * wavelength_m / (-4.0 * np.pi)) * 100.0

        # 5. Build geotransform from grid coordinates
        dx = float(x[1] - x[0])
        dy = float(y[1] - y[0])
        
        # Ensure north-up orientation for GeoTIFF
        if dy > 0:
            los_cm = np.flipud(los_cm)
            y_top = float(y[-1]) + abs(dy) / 2.0
        else:
            y_top = float(y[0]) + abs(dy) / 2.0
            
        x_left = float(x[0]) - abs(dx) / 2.0
        transform = from_origin(x_left, y_top, abs(dx), abs(dy))

        # 6. Save full scene GeoTIFF first
        full_tif = PROCESSED_DIR / f"full_{track_label}_los_cm.tif"
        with rasterio.open(
            full_tif,
            "w",
            driver="GTiff",
            height=los_cm.shape[0],
            width=los_cm.shape[1],
            count=1,
            dtype="float32",
            crs=f"EPSG:{epsg}",
            transform=transform,
            nodata=np.nan,
            compress="lzw"
        ) as dst:
            dst.write(los_cm.astype("float32"), 1)

        # 7. Clip directly to Addis Ababa / AAU campuses
        aau_tif = PROCESSED_DIR / f"aau_{track_label}_los_cm.tif"
        with rasterio.open(full_tif) as src:
            window = from_bounds(*AAU_BBOX_UTM, transform=src.transform)
            clipped_data = src.read(1, window=window)
            clipped_transform = src.window_transform(window)
            
            # Normalize relative to median scene motion (removes bulk orbital ramp)
            clipped_data = clipped_data - np.nanmedian(clipped_data)

            profile = src.profile.copy()
            profile.update({
                "height": clipped_data.shape[0],
                "width": clipped_data.shape[1],
                "transform": clipped_transform
            })

            with rasterio.open(aau_tif, "w", **profile) as dst:
                dst.write(clipped_data, 1)

        print(f"  -> Saved AAU map: {aau_tif}")

def main():
    for track in ["ascending", "descending"]:
        files = sorted((RAW_DIR / track).glob("*.h5"))
        if not files:
            print(f"No .h5 files found in {RAW_DIR / track}")
            continue
        process_gunw_to_geotiff(files[0], track)

if __name__ == "__main__":
    main()