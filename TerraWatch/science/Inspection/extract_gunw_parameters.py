from pathlib import Path
import h5py
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FILE_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "nisar"
    / "descending"
    / "NISAR_L2_PR_GUNW_031_165_D_084_032_2000_SH_20260929T155015_20260929T155050_20261011T155015_20261011T155050_P05023_N_F_J_001.h5"
)

def format_attr(value):
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    return value

def find_dataset(h5, name):
    matches = []

    def visitor(path, obj):
        if isinstance(obj, h5py.Dataset):
            if path.split("/")[-1] == name:
                matches.append(path)

    h5.visititems(visitor)
    return sorted(matches)

def describe_dataset(h5, name):
    paths = find_dataset(h5, name)

    if not paths:
        print(f"\n{name}: NOT FOUND")
        return

    for path in paths:
        dataset = h5[path]

        print(f"\n{name}")
        print(f"  Path: {path}")
        print(f"  Shape: {dataset.shape}")
        print(f"  Type: {dataset.dtype}")

        for key in ["units", "description", "long_name"]:
            if key in dataset.attrs:
                print(f"  {key}: {format_attr(dataset.attrs[key])}")

        if dataset.size <= 10:
            val = dataset[()]
            print(f"  Values: {format_attr(val)}")

def main():
    if not FILE_PATH.is_file():
        print(f"File not found: {FILE_PATH}")
        return

    print("=" * 70)
    print("TERRAWATCH | GUNW PARAMETER EXTRACTION")
    print("=" * 70)
    print(f"Target File: {FILE_PATH.name}")

    with h5py.File(FILE_PATH, "r") as h5:

        # 1. Geographic coordinates (handles multiple frequencies if present)
        print("\n" + "=" * 70)
        print("SPATIAL COORDINATES & GRID")
        print("=" * 70)

        for name in ["xCoordinates", "yCoordinates"]:
            paths = find_dataset(h5, name)

            if not paths:
                print(f"\n{name}: NOT FOUND")
                continue

            for path in paths:
                values = np.asarray(h5[path][()]).astype(float)

                print(f"\n{name} ({path})")
                print(f"  Minimum: {np.nanmin(values):.4f}")
                print(f"  Maximum: {np.nanmax(values):.4f}")
                print(f"  Number of coordinates: {values.size}")

                differences = np.diff(values)
                print(f"  First coordinate difference: {differences[0]:.4f}")
                print(
                    f"  Median coordinate spacing: "
                    f"{np.nanmedian(np.abs(differences)):.4f} m"
                )

        # 2. Radar frequency and wavelength
        print("\n" + "=" * 70)
        print("RADAR PARAMETERS")
        print("=" * 70)

        freq_paths = find_dataset(h5, "centerFrequency")

        if freq_paths:
            for path in freq_paths:
                frequency = float(np.asarray(h5[path][()]).squeeze())
                wavelength = 299792458.0 / frequency

                print(f"\nPath: {path}")
                print(f"  Center frequency: {frequency:.6f} Hz")
                print(f"  Wavelength: {wavelength:.8f} m")
                print(f"  Wavelength: {wavelength * 100:.4f} cm")
        else:
            print("\ncenterFrequency: NOT FOUND")

        # 3. Projection & Viewing Geometry
        print("\n" + "=" * 70)
        print("PROJECTION & GEOMETRY DATASETS")
        print("=" * 70)

        for name in [
            "projection",
            "incidenceAngle",
            "lookAngle",
            "losUnitVectorX",
            "losUnitVectorY",
            "losUnitVectorZ",
        ]:
            describe_dataset(h5, name)

        # 4. Important interferometric datasets
        print("\n" + "=" * 70)
        print("INTERFEROGRAM DATASETS")
        print("=" * 70)

        for name in [
            "unwrappedPhase",
            "coherenceMagnitude",
            "connectedComponents",
            "wrappedInterferogram",
            "ionospherePhaseScreen",
            "ionospherePhaseScreenUncertainty",
        ]:
            describe_dataset(h5, name)

        # 5. Phase correction datasets
        print("\n" + "=" * 70)
        print("PHASE CORRECTION DATASETS")
        print("=" * 70)

        for name in [
            "hydrostaticTroposphericPhaseScreen",
            "wetTroposphericPhaseScreen",
            "slantRangeSolidEarthTidesPhase",
        ]:
            describe_dataset(h5, name)

        # 6. Product identification metadata
        print("\n" + "=" * 70)
        print("IDENTIFICATION METADATA")
        print("=" * 70)

        identification = "science/LSAR/identification"

        if identification in h5:
            group = h5[identification]

            for key, value in group.attrs.items():
                print(f"{key}: {format_attr(value)}")

            for name in [
                "boundingPolygon",
                "productVersion",
                "productSpecificationVersion",
                "productAccuracy",
                "productLevel",
                "orbitPassDirection",
            ]:
                if name in group:
                    value = format_attr(group[name][()])
                    print(f"{name}: {str(value)[:500]}")

    print("\nExtraction completed successfully.")

if __name__ == "__main__":
    main()