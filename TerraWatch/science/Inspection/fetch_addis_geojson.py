from pathlib import Path
import osmnx as ox

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FINAL_DIR = PROJECT_ROOT / "data" / "final"
FINAL_DIR.mkdir(parents=True, exist_ok=True)

# Configure OSMnx to cache requests and avoid timeouts
ox.settings.use_cache = True
ox.settings.timeout = 180

# 1. Fetch Official Addis Ababa Outer City Boundary
print("1. Downloading Addis Ababa city boundary...")
city_gdf = ox.geocode_to_gdf("Addis Ababa, Ethiopia")
city_out = FINAL_DIR / "addis_ababa_city_boundary.geojson"
city_gdf[["display_name", "geometry"]].to_file(city_out, driver="GeoJSON")
print(f"   -> Saved city boundary to: {city_out}")

# 2. Fetch Sub-City (Kifle Ketema) Administrative Polygons
print("2. Downloading Addis Ababa sub-city boundaries...")
subcities = ox.features_from_place(
    "Addis Ababa, Ethiopia",
    tags={"boundary": "administrative", "admin_level": ["6", "8"]}
)
subcities = subcities[subcities.geometry.type.isin(["Polygon", "MultiPolygon"])].copy()
sub_cols = [c for c in ["name", "name:en", "admin_level", "geometry"] if c in subcities.columns]
subcities_out = FINAL_DIR / "addis_ababa_subcities.geojson"
subcities[sub_cols].to_file(subcities_out, driver="GeoJSON")
print(f"   -> Saved {len(subcities)} sub-city polygons to: {subcities_out}")

# 3. Fetch Major Roads, Highways, Bridges & Light Rail
print("3. Downloading arterial roads, bridges, and light rail...")
infra = ox.features_from_place(
    "Addis Ababa, Ethiopia",
    tags={
        "highway": ["motorway", "trunk", "primary", "secondary"],
        "bridge": "yes",
        "railway": "light_rail",
    }
)
infra = infra[infra.geometry.type.isin(["LineString", "MultiLineString", "Polygon"])].copy()
infra_cols = [c for c in ["name", "highway", "bridge", "railway", "geometry"] if c in infra.columns]
infra_out = FINAL_DIR / "addis_ababa_roads_bridges.geojson"
infra[infra_cols].to_file(infra_out, driver="GeoJSON")
print(f"   -> Saved {len(infra):,} road/bridge segments to: {infra_out}")
