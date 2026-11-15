
from pathlib import Path

import h5py
from shapely import wkt
from shapely.geometry import Point
from pyproj import Transformer

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FILE_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "nisar"
    / "descending"
    / "NISAR_L2_PR_GUNW_031_165_D_084_032_2000_SH_20260929T155015_20260929T155050_20261011T155015_20261011T155050_P05023_N_F_J_001.h5"
)

# Approximate Addis Ababa reference point
ADDIS_LON = 38.74689
ADDIS_LAT = 9.02497

def main():
    with h5py.File(FILE_PATH, "r") as h5:

        polygon_raw = h5[
            "science/LSAR/identification/boundingPolygon"
        ][()]

        if isinstance(polygon_raw, bytes):
            polygon_raw = polygon_raw.decode("utf-8")

        footprint = wkt.loads(polygon_raw)

        print("=" * 65)
        print("TERRAWATCH | NISAR COVERAGE CHECK")
        print("=" * 65)

        print("\nCOMPLETE PRODUCT FOOTPRINT:")
        print(polygon_raw)

        print("\nFOOTPRINT BOUNDS:")
        print(footprint.bounds)

        addis_point = Point(ADDIS_LON, ADDIS_LAT)

        print("\nADDIS ABABA CENTER:")
        print(f"Longitude: {ADDIS_LON}")
        print(f"Latitude:  {ADDIS_LAT}")

        print("\nCENTER COVERAGE TEST:")
        print("Inside footprint:", footprint.covers(addis_point))

        # Convert Addis center into the product's UTM coordinate system
        transformer = Transformer.from_crs(
            "EPSG:4326",
            "EPSG:32637",
            always_xy=True
        )

        x, y = transformer.transform(ADDIS_LON, ADDIS_LAT)

        print("\nADDIS CENTER IN PRODUCT CRS (EPSG:32637):")
        print(f"Easting:  {x:.2f} m")
        print(f"Northing: {y:.2f} m")

        grid = "science/LSAR/GUNW/grids/frequencyA/unwrappedInterferogram"

        x_coords = h5[f"{grid}/xCoordinates"][:]
        y_coords = h5[f"{grid}/yCoordinates"][:]

        print("\nRASTER GRID EXTENT:")
        print(f"X: {x_coords.min():.2f} to {x_coords.max():.2f}")
        print(f"Y: {y_coords.min():.2f} to {y_coords.max():.2f}")

        in_grid = (
            x_coords.min() <= x <= x_coords.max()
            and y_coords.min() <= y <= y_coords.max()
        )

        print("\nCENTER INSIDE RECTANGULAR GRID:", in_grid)

        print("\nCoverage inspection completed.")

if __name__ == "__main__":
    main()
