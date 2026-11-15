import json
import geopandas as gpd
from shapely.geometry import Point
from config import SUBCITY_RISK_GEOJSON, RISK_STRUCTURES_GEOJSON

class StructureService:
    def __init__(self):
        self.subcities_geojson = (
            json.loads(SUBCITY_RISK_GEOJSON.read_text(encoding="utf-8"))
            if SUBCITY_RISK_GEOJSON.exists()
            else {"type": "FeatureCollection", "features": []}
        )
        self.structures_geojson = (
            json.loads(RISK_STRUCTURES_GEOJSON.read_text(encoding="utf-8"))
            if RISK_STRUCTURES_GEOJSON.exists()
            else {"type": "FeatureCollection", "features": []}
        )

        if RISK_STRUCTURES_GEOJSON.exists():
            gdf = gpd.read_file(RISK_STRUCTURES_GEOJSON)
            self.structures_utm = gdf.to_crs("EPSG:32637")
        else:
            self.structures_utm = None

    def find_structures_near(self, lat: float, lon: float, radius_m: float = 150.0, limit: int = 8):
        if self.structures_utm is None or self.structures_utm.empty:
            return []

        pt_utm = next(iter(gpd.GeoSeries([Point(lon, lat)], crs="EPSG:4326").to_crs("EPSG:32637")))
        dists = self.structures_utm.geometry.distance(pt_utm)
        nearby = self.structures_utm[dists <= radius_m].copy()
        nearby = nearby.sort_values("vertical_cm", ascending=True).head(limit)

        results = []
        for _, row in nearby.iterrows():
            results.append({
                "display_name": str(row.get("display_name", "Exposed Structure")),
                "structure_type": str(row.get("structure_type", "Infrastructure")),
                "vertical_cm": float(row.get("vertical_cm", 0.0)),
                "risk_level": str(row.get("risk_level", "Moderate Risk")),
            })
        return results

    def get_top_at_risk(self, limit: int = 10):
        features = self.structures_geojson.get("features", [])
        sorted_feats = sorted(
            features,
            key=lambda f: f.get("properties", {}).get("vertical_cm", 0.0),
        )[:limit]
        summary = []
        for f in sorted_feats:
            props = f.get("properties", {})
            geom = f.get("geometry", {})
            coords = geom.get("coordinates", [])
            # Extract representative [lon, lat] for map zoom
            lon, lat = 38.765, 8.995
            if geom.get("type") == "Point" and len(coords) >= 2:
                lon, lat = coords[0], coords[1]
            elif geom.get("type") == "LineString" and coords:
                lon, lat = coords[0][0], coords[0][1]
            elif geom.get("type") == "Polygon" and coords and coords[0]:
                lon, lat = coords[0][0][0], coords[0][0][1]
            elif geom.get("type") == "MultiPolygon" and coords and coords[0] and coords[0][0]:
                lon, lat = coords[0][0][0][0], coords[0][0][0][1]

            summary.append({
                "display_name": props.get("display_name", "Exposed Structure"),
                "structure_type": props.get("structure_type", "Infrastructure"),
                "vertical_cm": props.get("vertical_cm"),
                "risk_level": props.get("risk_level"),
                "lat": round(lat, 5),
                "lon": round(lon, 5),
            })
        return summary
