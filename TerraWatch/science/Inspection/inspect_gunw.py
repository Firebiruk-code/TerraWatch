
from pathlib import Path
import argparse
import h5py
import os
import sys

# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

# Automatically identify the TerraWatch project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIRECTORY = PROJECT_ROOT / "data" / "raw" / "nisar"

# Keywords that may identify important GUNW datasets.
IMPORTANT_KEYWORDS = [
    "unwrappedphase",
    "coherencemagnitude",
    "connectedcomponents",
    "latitude",
    "longitude",
    "incidenceangle",
    "lookangle",
    "los",
    "slant",
    "wavelength",
    "reference",
    "perpendicularbaseline",
    "alongtrackbaseline",
]

# --------------------------------------------------
# FILE DISCOVERY
# --------------------------------------------------

def discover_files():

    files = list(DATA_DIRECTORY.rglob("*.h5"))

    # Prefer descending products for the first inspection.
    descending = [
        f for f in files
        if "descending" in str(f).lower()
    ]

    ascending = [
        f for f in files
        if "ascending" in str(f).lower()
    ]

    return sorted(descending) + sorted(ascending)

# --------------------------------------------------
# DATASET IDENTIFICATION
# --------------------------------------------------

def is_important(name):

    name_lower = name.lower()

    return any(
        keyword in name_lower
        for keyword in IMPORTANT_KEYWORDS
    )

# --------------------------------------------------
# HDF5 INSPECTION
# --------------------------------------------------

def inspect_hdf5(filepath):

    filepath = Path(filepath)

    print("\n" + "=" * 90)
    print("TERRAWATCH | NISAR GUNW PRODUCT INSPECTOR")
    print("=" * 90)

    print(f"\nFile: {filepath.name}")
    print(f"Size: {filepath.stat().st_size / (1024**2):.2f} MB")

    important_datasets = []
    total_datasets = 0
    total_groups = 0

    try:

        with h5py.File(filepath, "r") as f:

            print("\nROOT ATTRIBUTES")
            print("-" * 90)

            for key, value in f.attrs.items():
                print(f"{key}: {value}")

            print("\nHDF5 STRUCTURE")
            print("-" * 90)

            def visitor(name, obj):

                nonlocal total_datasets, total_groups

                if isinstance(obj, h5py.Group):

                    total_groups += 1
                    print(f"\n[GROUP] {name}")

                elif isinstance(obj, h5py.Dataset):

                    total_datasets += 1

                    print(f"\n[DATASET] {name}")
                    print(f"  Shape: {obj.shape}")
                    print(f"  Type: {obj.dtype}")
                    print(f"  Size: {obj.size:,} elements")

                    if is_important(name):

                        important_datasets.append(name)

                        print("  >>> POTENTIALLY IMPORTANT FOR TERRAWATCH <<<")

                    # Print dataset attributes.
                    if obj.attrs:

                        print("  Attributes:")

                        for key, value in obj.attrs.items():

                            print(f"    {key}: {value}")

            f.visititems(visitor)

            print("\n" + "=" * 90)
            print("INSPECTION SUMMARY")
            print("=" * 90)

            print(f"Total groups: {total_groups}")
            print(f"Total datasets: {total_datasets}")

            print("\nIMPORTANT DATASET CANDIDATES")

            for dataset in important_datasets:
                print(f"  - {dataset}")

            print("\nInspection completed successfully.")

    except OSError as error:

        print("\nERROR: Could not open this file as HDF5.")
        print(error)

        return False

    return True

# --------------------------------------------------
# MAIN PROGRAM
# --------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description="Inspect NISAR GUNW HDF5 products."
    )

    parser.add_argument(
        "filepath",
        nargs="?",
        help="Optional path to a specific NISAR .h5 file."
    )

    args = parser.parse_args()

    if args.filepath:

        filepath = Path(args.filepath)

        if not filepath.is_absolute():
            filepath = PROJECT_ROOT / filepath

        if not filepath.is_file():

            print(f"File not found: {filepath}")
            sys.exit(1)

        inspect_hdf5(filepath)

    else:

        files = discover_files()

        if not files:

            print("No .h5 files were found.")
            print(f"Search directory: {DATA_DIRECTORY}")
            print("\nCheck that your NISAR files are inside:")
            print("data/raw/nisar/ascending/")
            print("data/raw/nisar/descending/")

            sys.exit(1)

        print(f"\nFound {len(files)} NISAR HDF5 files.")

        print("\nAvailable files:")

        for index, file in enumerate(files, start=1):
            print(f"{index}. {file.name}")

        # Inspect the first descending file by default.
        print("\nInspecting the first available descending product...")

        success = inspect_hdf5(files[0])

        if not success:
            sys.exit(1)

if __name__ == "__main__":
    main()