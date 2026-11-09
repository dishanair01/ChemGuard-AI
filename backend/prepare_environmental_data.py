
import pandas as pd
from pathlib import Path

# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = DATA_DIR / "processed"

FILE = DATA_DIR / "pharms-uba_v3_2021_0.xlsx"


def prepare_database():

    print("\n===== CHEMGUARD AI =====")
    print("ENVIRONMENTAL DATA PREPARATION")
    print("==============================")

    if not FILE.exists():
        print("ERROR: Dataset not found:", FILE)
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        print("\nLoading environmental measurements...")

        # Third Excel row contains the detailed column headers
        mec = pd.read_excel(
            FILE,
            sheet_name="MEC_global_v3",
            header=2,
            engine="openpyxl"
        )

        # Pharmaceutical reference sheet starts at the first row
        pharma = pd.read_excel(
            FILE,
            sheet_name="Pharma_Agents_v3",
            header=0,
            engine="openpyxl"
        )

        # Clean column names without changing their meaning
        mec.columns = mec.columns.astype(str).str.strip()
        pharma.columns = pharma.columns.astype(str).str.strip()

        # Remove completely empty rows
        mec = mec.dropna(how="all")
        pharma = pharma.dropna(how="all")

        # Remove accidental whitespace from text fields
        for df in [mec, pharma]:
            for column in df.select_dtypes(include=["object", "str"]).columns:
                df[column] = df[column].map(
                    lambda value: value.strip()
                    if isinstance(value, str) else value
                )

        # Save cleaned research tables
        mec_output = OUTPUT_DIR / "environmental_measurements.csv"
        pharma_output = OUTPUT_DIR / "pharmaceutical_reference.csv"

        mec.to_csv(
            mec_output,
            index=False,
            encoding="utf-8-sig"
        )

        pharma.to_csv(
            pharma_output,
            index=False,
            encoding="utf-8-sig"
        )

        print("\n===== PREPARATION RESULTS =====")

        print("\nEnvironmental measurements")
        print("Records:", len(mec))
        print("Columns:", len(mec.columns))

        print("\nPharmaceutical reference")
        print("Records:", len(pharma))
        print("Columns:", len(pharma.columns))

        print("\nEnvironmental columns:")
        for column in mec.columns:
            print("-", column)

        print("\nPharmaceutical columns:")
        for column in pharma.columns:
            print("-", column)

        print("\n===== OUTPUT FILES =====")
        print(mec_output)
        print(pharma_output)

        print("\nFirst 5 environmental records:")
        print(
            mec[
                ["Name of Analyte", "CAS number", "Matrix",
                 "Sampling Country", "MEC standardized", "Unit standard"]
            ].head().to_string(index=False)
        )

        print("\nDATABASE PREPARATION COMPLETED!")

    except Exception as error:
        print("\nPreparation failed:", error)


if __name__ == "__main__":
    prepare_database()
