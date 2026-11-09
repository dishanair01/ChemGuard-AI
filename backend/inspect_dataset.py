
import pandas as pd
from pathlib import Path

# Locate the project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Locate the Excel dataset
DATA_FILE = BASE_DIR / "data" / "pharms-uba_v3_2021_0.xlsx"

def inspect_dataset():

    print("\n===== CHEMGUARD AI =====")
    print("ENVIRONMENTAL DATASET INSPECTOR")
    print("===============================")

    if not DATA_FILE.exists():
        print("\nERROR: Dataset file not found!")
        print("Expected location:", DATA_FILE)
        return

    try:
        excel = pd.ExcelFile(DATA_FILE)

        print("\nAvailable sheets:")
        for sheet in excel.sheet_names:
            print("-", sheet)

        for sheet in excel.sheet_names:

            print("\n" + "=" * 50)
            print("SHEET:", sheet)
            print("=" * 50)

            df = pd.read_excel(
                 DATA_FILE,
                 sheet_name=sheet,
                 header=None,
                 nrows=8
            )

            print("\nRAW FIRST 8 ROWS:")
            print(df.to_string(index=False, header=False))

            print("\nColumn names:")
            for column in df.columns:
                print("-", column)

            print("\nFirst 5 records:")
            print(df.head().to_string(index=False))

            print("\nData types:")
            print(df.dtypes.to_string())

            print("\nMissing values in inspected rows:")
            print(df.isnull().sum().to_string())

    except Exception as error:
        print("\nDataset inspection failed:", error)


if __name__ == "__main__":
    inspect_dataset()
