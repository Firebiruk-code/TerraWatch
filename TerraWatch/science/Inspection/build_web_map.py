from pathlib import Path
import folium
import matplotlib
matplotlib.use("Agg")
import matplotlib.colors as colors
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FINAL_DIR = PROJECT_ROOT / "data" / "final"
tif_path = FINAL_DIR / "addis_ababa_vertical_displacement_cm.tif"
html_out = FINAL_DIR / "addis_ababa_insar_map.html"

def remove_planar_ramp(arr):
    """Fits and subtracts a 2D linear plane to remove atmospheric/orbital tilt."""
    rows, cols = arr.shape
    y_grid, x_grid = np.mgrid[0:rows, 0:cols]
    valid = ~np.isnan(arr)
    
    # Solve z = a*x + b*y + c on valid pixels
    A = np.column_stack([x_grid[valid], y_grid[valid], np.ones(np.count_nonzero(valid))])
    coeffs, _, _, _ = np.linalg.lstsq(A, arr[valid], rcond=None)
    a, b, c = coeffs
    
    ramp = a * x_grid + b * y_grid + c
    return arr - ramp

# 1. Load GeoTIFF, remove regional orbital/atmospheric ramp, and reproject to WGS84
with rasterio.open(tif_path) as src:
    raw_vertical = src.read(1)
    detrended_vertical = remove_planar_ramp(raw_vertical)
    
    dst_crs = "EPSG:4326"
    transform, width, height = calculate_default_transform(
        src.crs, dst_crs, src.width, src.height, *src.bounds
    )
    data_wgs84 = np.empty((height, width), dtype=np.float32)
    reproject(
        source=detrended_vertical,
        destination=data_wgs84,
        src_transform=src.transform,
        src_crs=src.crs,
        dst_transform=transform,
        dst_crs=dst_crs,
        resampling=Resampling.bilinear,
        src_nodata=np.nan,
        dst_nodata=np.nan,
    )
    west, south, east, north = rasterio.transform.array_bounds(height, width, transform)

# 2. Colorize localized displacement (-1.5 cm sinking = Red, 0 = Transparent/White, +1.5 cm uplift = Blue)
V_LIMIT = 1.5
norm = colors.Normalize(vmin=-V_LIMIT, vmax=V_LIMIT)
cmap = matplotlib.colormaps["RdBu"]
rgba_img = cmap(norm(np.clip(data_wgs84, -V_LIMIT, V_LIMIT)))

# Make near-zero background slightly more transparent so city streets show through clearly
alpha = np.where(np.isnan(data_wgs84), 0.0, 0.65)
rgba_img[..., 3] = alpha

# 3. Build interactive map with clean, watermark-free Esri basemaps
m = folium.Map(location=[8.995, 38.765], zoom_start=11, tiles=None)

folium.TileLayer(
    tiles="https://arcgisonline.com{z}/{y}/{x}",
    attr="Esri World Street Map",
    name="Street Map",
    overlay=False,
    control=True,
).add_to(m)

folium.TileLayer(
    tiles="https://arcgisonline.com{z}/{y}/{x}",
    attr="Esri World Imagery",
    name="Satellite Basemap",
    overlay=False,
    control=True,
).add_to(m)

folium.raster_layers.ImageOverlay(
    image=rgba_img,
    bounds=[[south, west], [north, east]],
    opacity=0.85,
    name="Localized Vertical Motion (cm)",
).add_to(m)

# Add key Addis Ababa reference & hydrogeological landmarks
landmarks = [
    ("Central Addis Ababa (Piassa / Churchill)", 9.0300, 38.7520),
    ("Bole International Airport & Urban Core", 8.9779, 38.7993),
    ("Akaki-Kality Wellfield (Major Groundwater Zone)", 8.8850, 38.7850),
    ("Kilinto Industrial & Science Hub", 8.8872, 38.8094),
    ("Entoto Mountain Ridge (Northern Bedrock)", 9.0830, 38.7610),
    ("AAU Main Campus (Sidist Kilo)", 9.0468, 38.7592),
]

for name, lat, lon in landmarks:
    folium.Marker(
        [lat, lon],
        popup=f"<b>{name}</b>",
        tooltip=name,
        icon=folium.Icon(color="cadetblue", icon="info-sign"),
    ).add_to(m)

legend_html = f"""
<div style="position: fixed; bottom: 30px; right: 30px; width: 240px; z-index:9999;
            background-color: white; border: 2px solid #ccc; border-radius: 6px;
            padding: 10px; font-family: Arial, sans-serif; font-size: 12px; box-shadow: 2px 2px 6px rgba(0,0,0,0.2);">
    <b>TerraWatch | NISAR InSAR</b><br>
    <i>Detrended Vertical Motion (cm)</i><br><br>
    <div style="background: linear-gradient(to right, #b2182b, #f7f7f7, #2166ac); height: 14px; width: 100%; border-radius: 3px;"></div>
    <div style="display: flex; justify-content: space-between; margin-top: 4px;">
        <span>-{V_LIMIT} cm (Sinking)</span>
        <span>0</span>
        <span>+{V_LIMIT} cm (Uplift)</span>
    </div>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

folium.LayerControl().add_to(m)
m.save(str(html_out))
print(f"Updated detrended map saved to: {html_out}")
