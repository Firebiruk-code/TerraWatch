import numpy as np
from rasterio.warp import transform as warp_transform
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest

class SpatialMLService:
    def __init__(self, utm_data: np.ndarray, utm_transform, utm_crs):
        self.utm_data = utm_data
        self.utm_transform = utm_transform
        self.utm_crs = utm_crs
        self.anomaly_grid = np.full_like(utm_data, np.nan, dtype=np.float32)
        self.clusters = []
        self._fit_models()

    def _fit_models(self):
        valid_mask = ~np.isnan(self.utm_data)
        rows, cols = np.where(valid_mask)
        vals = self.utm_data[valid_mask]

        if vals.size < 50:
            return

        # 1. Isolation Forest: Detects abnormal localized ground shifts across Addis Ababa
        h, w = self.utm_data.shape
        X_all = np.column_stack([rows / h, cols / w, vals])
        iso = IsolationForest(contamination=0.05, random_state=42, n_jobs=-1)
        iso.fit(X_all)

        raw_scores = -iso.decision_function(X_all)
        norm_scores = (raw_scores - raw_scores.min()) / (raw_scores.max() - raw_scores.min() + 1e-6)
        self.anomaly_grid[valid_mask] = np.round(norm_scores * 100.0, 1)

        # 2. DBSCAN Clustering: Groups contiguous sinking pixels (<= -0.45 cm) into coherent basins
        sink_mask = valid_mask & (self.utm_data <= -0.45)
        s_rows, s_cols = np.where(sink_mask)
        s_vals = self.utm_data[sink_mask]

        if s_vals.size >= 5:
            coords_px = np.column_stack([s_rows, s_cols])
            db = DBSCAN(eps=2.5, min_samples=4).fit(coords_px)

            for cid in sorted(set(db.labels_)):
                if cid == -1:
                    continue
                c_mask = db.labels_ == cid
                c_rows, c_cols, c_vals = s_rows[c_mask], s_cols[c_mask], s_vals[c_mask]

                mean_r, mean_c = float(np.mean(c_rows)), float(np.mean(c_cols))
                x_utm, y_utm = self.utm_transform * (mean_c, mean_r)
                lons, lats = warp_transform(self.utm_crs, "EPSG:4326", [x_utm], [y_utm])

                area_km2 = round((c_vals.size * 80 * 80) / 1_000_000, 2)
                self.clusters.append({
                    "cluster_id": int(cid + 1),
                    "center_lat": round(float(lats[0]), 5),
                    "center_lon": round(float(lons[0]), 5),
                    "pixel_count": int(c_vals.size),
                    "area_km2": area_km2,
                    "mean_sinking_cm": round(float(np.mean(c_vals)), 2),
                    "peak_sinking_cm": round(float(np.min(c_vals)), 2),
                })

            self.clusters.sort(key=lambda item: item["peak_sinking_cm"])

    def get_pixel_anomaly_score(self, r: int, c: int) -> float | None:
        h, w = self.anomaly_grid.shape
        if 0 <= r < h and 0 <= c < w and not np.isnan(self.anomaly_grid[r, c]):
            return float(self.anomaly_grid[r, c])
        return None
