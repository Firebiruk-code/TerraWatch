import base64
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.colors as colors
import numpy as np
from PIL import Image
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling, transform as warp_transform
from backend.config import DETRENDED_TIF, RAW_VERT_TIF, COLOR_LIMIT_CM, RADAR_RESOLUTION_M

def _remove_planar_ramp(arr: np.ndarray) -> np.ndarray:
    rows, cols = arr.shape
    y_grid, x_grid = np.mgrid[0:rows, 0:cols]
    valid = ~np.isnan(arr)
    A = np.column_stack([x_grid[valid], y_grid[valid], np.ones(np.count_nonzero(valid))])
    coeffs, _, _, _ = np.linalg.lstsq(A, arr[valid], rcond=None)
    a, b, c = coeffs
    return arr - (a * x_grid + b * y_grid + c)

class RadarService:
    def __init__(self):
        active_tif = DETRENDED_TIF if DETRENDED_TIF.exists() else RAW_VERT_TIF
        with rasterio.open(active_tif) as src:
            arr = src.read(1).astype(np.float32)
            if active_tif == RAW_VERT_TIF:
                arr = _remove_planar_ramp(arr)
            self.utm_data = arr
            self.utm_transform = src.transform
            self.utm_crs = src.crs

            # Reproject once to WGS84 for crisp Leaflet map overlay
            dst_crs = "EPSG:4326"
            wgs_transform, w_width, w_height = calculate_default_transform(
                src.crs, dst_crs, src.width, src.height, *src.bounds
            )
            wgs_data = np.empty((w_height, w_width), dtype=np.float32)
            reproject(
                source=self.utm_data,
                destination=wgs_data,
                src_transform=self.utm_transform,
                src_crs=self.utm_crs,
                dst_transform=wgs_transform,
                dst_crs=dst_crs,
                resampling=Resampling.nearest,
                src_nodata=np.nan,
                dst_nodata=np.nan,
            )
            west, south, east, north = rasterio.transform.array_bounds(w_height, w_width, wgs_transform)
            self.bounds = [[south, west], [north, east]]

        # Pre-render transparent PNG overlay in memory
        norm = colors.Normalize(vmin=-COLOR_LIMIT_CM, vmax=COLOR_LIMIT_CM)
        cmap = matplotlib.colormaps["RdBu"]
        rgba = (cmap(norm(np.clip(wgs_data, -COLOR_LIMIT_CM, COLOR_LIMIT_CM))) * 255).astype(np.uint8)
        rgba[..., 3] = np.where(np.isnan(wgs_data), 0, 185)

        buf = io.BytesIO()
        Image.fromarray(rgba, mode="RGBA").save(buf, format="PNG")
        self.overlay_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    def get_overlay_payload(self):
        return {
            "image_data_url": f"data:image/png;base64,{self.overlay_b64}",
            "bounds": self.bounds,
            "v_limit_cm": COLOR_LIMIT_CM,
            "resolution_m": RADAR_RESOLUTION_M,
        }

    def sample_point(self, lat: float, lon: float, radius_px: int = 2):
        xs, ys = warp_transform("EPSG:4326", self.utm_crs, [lon], [lat])
        col, row = ~self.utm_transform * (xs[0], ys[0])
        r, c = int(round(row)), int(round(col))

        h, w = self.utm_data.shape
        if not (0 <= r < h and 0 <= c < w):
            return None

        cell_val = self.utm_data[r, c]
        patch = self.utm_data[max(0, r - radius_px):r + radius_px + 1,
                              max(0, c - radius_px):c + radius_px + 1]
        valid = patch[~np.isnan(patch)]

        if np.isnan(cell_val) or valid.size == 0:
            return {"coherent": False, "row": r, "col": c}

        return {
            "coherent": True,
            "row": r,
            "col": c,
            "cell_cm": round(float(cell_val), 2),
            "mean_cm": round(float(np.mean(valid)), 2),
            "std_cm": round(float(np.std(valid)), 2) if valid.size > 1 else 0.15,
        }
