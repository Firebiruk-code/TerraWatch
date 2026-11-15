from pathlib import Path
import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import geometry_mask

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FINAL_DIR = PROJECT_ROOT / "data" / "final"

CLEAN_TIF = FINAL_DIR / "addis_ababa_vertical_detrended.tif"
SUBCITIES_IN = FINAL_DIR / "addis_ababa_subcities.geojson"
STRUCTURES_IN = FINAL_DIR / "addis_ababa_structures.geojson"

SUBCITY_RISK_OUT = FINAL_DIR / "addis_subcity_risk.geojson"
RISK_STRUCTURES_OUT = FINAL_DIR / "addis_at_risk_structures.geojson"

with rasterio.open(CLEAN_TIF) as src:
    detrended_arr = src.read(1)
    radar_transform = src.transform
    radar_crs = src.crs

    # 1. Calculate Sinking Statistics per Sub-City (Kifle Ketema)
    subcities = gpd.read_file(SUBCITIES_IN).to_crs(radar_crs)
    mean_vals, hotspot_vals = [], []

    for geom in subcities.geometry:
        mask = geometry_mask([geom], transform=radar_transform, invert=True, out_shape=detrended_arr.shape)
        pixels = detrended_arr[mask]
        valid = pixels[~np.isnan(pixels)]
        if valid.size > 0:
            mean_vals.append(round(float(np.mean(valid)), 2))
            hotspot_vals.append(round(float(np.percentile(valid, 5)), 2))
        else:
            mean_vals.append(None)
            hotspot_vals.append(None)

    subcities["mean_vertical_cm"] = mean_vals
    subcities["hotspot_sinking_cm"] = hotspot_vals
    subcities = subcities.to_crs("EPSG:4326")
    subcities.to_file(SUBCITY_RISK_OUT, driver="GeoJSON")
    print(f"1. Saved sub-city risk rankings: {SUBCITY_RISK_OUT.name}")

    # 2. Sample Detrended Radar Beneath Every Bridge, Road, Light Rail & Major Building
    structures = gpd.read_file(STRUCTURES_IN)
    struct_proj = structures.to_crs(radar_crs)
    centroids = struct_proj.geometry.centroid
    coords = [(pt.x, pt.y) for pt in centroids]
    sampled = [next(iter(val)) for val in src.sample(coords)]

structures["vertical_cm"] = [None if np.isnan(v) else round(float(v), 2) for v in sampled]

# Keep structures sitting in measurable sinking zones (<= -0.25 cm over 12 days)
at_risk = structures[structures["vertical_cm"].notnull() & (structures["vertical_cm"] <= -0.25)].copy()
at_risk["risk_level"] = np.where(at_risk["vertical_cm"] <= -0.50, "High Risk", "Moderate Risk")
at_risk = at_risk.sort_values("vertical_cm", ascending=True)

at_risk.to_file(RISK_STRUCTURES_OUT, driver="GeoJSON")
print(f"2. Saved {len(at_risk):,} at-risk bridges, roads & buildings: {RISK_STRUCTURES_OUT.name}")

print("\nTop 10 Most Exposed Structures / Corridors in Addis Ababa:")
cols_to_show = [c for c in ["display_name", "name", "structure_type", "vertical_cm", "risk_level"] if c in at_risk.columns]
print(at_risk[cols_to_show].head(10).to_string(index=False))
