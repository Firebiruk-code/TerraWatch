
from pathlib import Path
import time
import geopandas as gpd
import numpy as np
import osmnx as ox

# ============================================================
# TERRAWATCH | ADDIS ABABA GEOGRAPHIC DATA ACQUISITION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FINAL_DIR = PROJECT_ROOT / "data" / "final"
FINAL_DIR.mkdir(parents=True, exist_ok=True)

CITY_OUT = FINAL_DIR / "addis_ababa_city_boundary.geojson"
SUBCITIES_OUT = FINAL_DIR / "addis_ababa_subcities.geojson"
STRUCTURES_OUT = FINAL_DIR / "addis_ababa_structures.geojson"

# Search extent: west, south, east, north
ADDIS_BBOX = (38.64, 8.83, 38.92, 9.11)

# ============================================================
# OSMNX CONFIGURATION
# ============================================================

ox.settings.use_cache = True
ox.settings.requests_timeout = 180
ox.settings.overpass_url = "https://overpass-api.de/api"

# ============================================================
# DOWNLOAD WITH RETRIES
# ============================================================

def download_with_retry(fetch_fn, label, retries=3):
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            print(
                f"\nDownloading {label} "
                f"(attempt {attempt}/{retries})..."
            )

            result = fetch_fn()

            if result is None or result.empty:
                raise ValueError(f"No features returned for {label}")

            print(f"Downloaded {len(result):,} features.")
            return result

        except Exception as error:
            last_error = error

            print(
                f"Error: {type(error).__name__}: {error}"
            )

            if attempt < retries:
                wait = 4 * attempt
                print(f"Retrying in {wait} seconds...")
                time.sleep(wait)

    raise RuntimeError(
        f"Failed to download {label} after {retries} attempts."
    ) from last_error


# ============================================================
# GEOMETRY HELPERS
# ============================================================

def prepare_geometries(gdf):
    """Validate geometries and remove empty or unusable features."""

    if gdf.empty:
        return gdf

    gdf = gdf.copy()

    if gdf.crs is None:
        raise ValueError("Dataset has no CRS.")

    gdf = gdf.to_crs("EPSG:4326")

    gdf = gdf[
        gdf.geometry.notna()
        & ~gdf.geometry.is_empty
    ].copy()

    gdf["geometry"] = gdf.geometry.make_valid()

    return gdf


def polygon_features(gdf):
    """Keep polygon and multipolygon geometries."""

    return gdf[
        gdf.geometry.geom_type.isin(
            ["Polygon", "MultiPolygon"]
        )
    ].copy()


# ============================================================
# 1. ADDIS ABABA CITY BOUNDARY
# ============================================================

def get_city_boundary():

    if CITY_OUT.exists():
        print("\n1. Loading existing city boundary...")
        city = gpd.read_file(CITY_OUT)

    else:
        print("\n1. Downloading city boundary from Nominatim...")

        city = download_with_retry(
            lambda: ox.geocode_to_gdf(
                "Addis Ababa, Ethiopia"
            ),
            label="Addis Ababa city boundary"
        )

        city = prepare_geometries(city)
        city = polygon_features(city)

        if city.empty:
            raise ValueError(
                "Nominatim did not return a polygonal city boundary."
            )

        # Preserve useful attributes when available.
        columns = [
            c for c in [
                "display_name",
                "name",
                "name:en",
                "osm_type",
                "osm_id",
                "geometry"
            ]
            if c in city.columns
        ]

        city[columns].to_file(
            CITY_OUT,
            driver="GeoJSON"
        )

        print(f"Saved: {CITY_OUT}")

    city = prepare_geometries(city)
    city = polygon_features(city)

    if city.empty:
        raise ValueError("City boundary contains no polygons.")

    # Merge all returned city polygons into one study area.
    city = city.dissolve()

    print("City boundary loaded successfully.")
    print("Geometry:", city.geometry.iloc[0].geom_type)
    print("Bounds:", city.total_bounds)

    return city


# ============================================================
# 2. ADDIS ABABA SUB-CITIES
# ============================================================

def download_subcities(city):

    print("\n2. Downloading administrative boundaries...")

    subcities = download_with_retry(
        lambda: ox.features_from_bbox(
            bbox=ADDIS_BBOX,
            tags={
                "boundary": "administrative",
                "admin_level": ["5", "6"]
            }
        ),
        label="Addis Ababa administrative boundaries"
    )

    subcities = prepare_geometries(subcities)
    subcities = polygon_features(subcities)

    # Keep only features intersecting the city boundary.
    subcities = gpd.clip(subcities, city)

    if subcities.empty:
        print("WARNING: No sub-city polygons found.")
        return

    # Keep the original OSM attributes and geometry.
    subcities["geometry"] = subcities.geometry.make_valid()

    subcities.to_file(
        SUBCITIES_OUT,
        driver="GeoJSON"
    )

    print(f"Saved {len(subcities):,} administrative features.")
    print(f"Output: {SUBCITIES_OUT}")

    if "admin_level" in subcities.columns:
        print("\nAdministrative level counts:")
        print(subcities["admin_level"].value_counts(dropna=False))


# ============================================================
# 3. INFRASTRUCTURE AND STRUCTURES
# ============================================================

def download_infrastructure(city):

    print("\n3. Downloading infrastructure...")

    infrastructure_tags = {
        "highway": [
            "motorway",
            "trunk",
            "primary"
        ],

        "bridge": "yes",

        "railway": "light_rail",

        "building": [
            "industrial",
            "commercial",
            "hospital",
            "university",
            "public"
        ],

        "amenity": [
            "hospital",
            "university"
        ],

        "healthcare": "hospital"
    }

    infra = download_with_retry(
        lambda: ox.features_from_bbox(
            bbox=ADDIS_BBOX,
            tags=infrastructure_tags
        ),
        label="infrastructure and major structures"
    )

    infra = prepare_geometries(infra)

    # Keep relevant line and polygon geometries.
    infra = infra[
        infra.geometry.geom_type.isin([
            "LineString",
            "MultiLineString",
            "Polygon",
            "MultiPolygon"
        ])
    ].copy()

    # Clip features to the city boundary.
    infra = gpd.clip(infra, city)

    if infra.empty:
        print("WARNING: No infrastructure features found.")
        return

    # ========================================================
    # CLASSIFICATION
    # ========================================================

    def classify_structure(row):

        if str(row.get("bridge", "")) == "yes":
            return "Bridge / Overpass"

        if str(row.get("railway", "")) == "light_rail":
            return "Light Rail Line"

        if (
            str(row.get("healthcare", "")) == "hospital"
            or str(row.get("amenity", "")) == "hospital"
        ):
            return "Hospital"

        if str(row.get("amenity", "")) == "university":
            return "University"

        building = str(row.get("building", ""))

        if building not in ["", "nan", "None"]:
            return (
                "Building ("
                + building.replace("_", " ").title()
                + ")"
            )

        highway = str(row.get("highway", ""))

        if highway:
            return (
                "Major Road ("
                + highway.replace("_", " ").title()
                + ")"
            )

        return "Other Infrastructure"

    infra["structure_type"] = infra.apply(
        classify_structure,
        axis=1
    )

    # Create readable display names.
    if "name" in infra.columns:
        raw_names = infra["name"].fillna("").astype(str)
    else:
        raw_names = np.full(len(infra), "", dtype=object)

    infra["display_name"] = np.where(
        raw_names == "",
        infra["structure_type"],
        raw_names + " (" + infra["structure_type"] + ")"
    )

    # Keep useful source attributes.
    useful_columns = [
        "display_name",
        "structure_type",
        "name",
        "highway",
        "bridge",
        "railway",
        "building",
        "amenity",
        "healthcare",
        "geometry"
    ]

    keep_columns = [
        col for col in useful_columns
        if col in infra.columns
    ]

    infra[keep_columns].to_file(
        STRUCTURES_OUT,
        driver="GeoJSON"
    )

    print(f"Saved {len(infra):,} infrastructure features.")
    print(f"Output: {STRUCTURES_OUT}")

    print("\nInfrastructure classification:")
    print(infra["structure_type"].value_counts())


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 65)
    print("TERRAWATCH | ADDIS ABABA DATA ACQUISITION")
    print("=" * 65)

    city = get_city_boundary()

    download_subcities(city)

    download_infrastructure(city)

    print("\n" + "=" * 65)
    print("DATA ACQUISITION COMPLETED")
    print("=" * 65)

    print("\nGenerated files:")

    for path in [
        CITY_OUT,
        SUBCITIES_OUT,
        STRUCTURES_OUT
    ]:
        if path.exists():
            print(
                f"{path.name}: "
                f"{path.stat().st_size / 1024:.2f} KB"
            )
        else:
            print(f"{path.name}: NOT GENERATED")


if __name__ == "__main__":
    main()
