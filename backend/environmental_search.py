
import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "environmental_measurements.csv.gz"
)


def search_environmental_records(compound_name):

    if not DATA_FILE.exists():
        return {"error": "Environmental database not found"}

    try:
        df = pd.read_csv(DATA_FILE, low_memory=False)

        analyte = df["Name of Analyte"].fillna("").astype(str).str.strip()

        # Exact parent compound match
        exact = df[
            analyte.str.casefold() == compound_name.strip().casefold()
        ].copy()

        # Other records whose names contain the search term
        related = df[
            analyte.str.contains(
                compound_name.strip(),
                case=False,
                regex=False,
                na=False
            )
            & (analyte.str.casefold() != compound_name.strip().casefold())
        ].copy()

        columns = [
            "Name of Analyte",
            "CAS number",
            "Matrix",
            "Sampling Location",
            "Sampling Country",
            "Sampling Period Start",
            "Sampling Period End",
            "Statistics",
            "Detection",
            "MEC standardized",
            "Unit standard",
            "Emission Source",
            "Literature Citation"
        ]

        exact_columns = [c for c in columns if c in exact.columns]
        related_columns = [c for c in columns if c in related.columns]

        return {
            "search_term": compound_name,
            "exact_count": len(exact),
            "related_count": len(related),
            "exact_records": exact[exact_columns],
            "related_records": related[related_columns]
        }

    except Exception as error:
        return {"error": str(error)}


if __name__ == "__main__":

    name = input("\nSearch pharmaceutical compound: ").strip()

    result = search_environmental_records(name)

    if "error" in result:
        print("ERROR:", result["error"])

    else:
        print("\n===== CHEMGUARD AI =====")
        print("ENVIRONMENTAL EVIDENCE")
        print("=======================")

        print("\nCompound:", result["search_term"])
        print("Exact parent-compound records:", result["exact_count"])
        print("Name-related records:", result["related_count"])

        print("\n===== EXACT COMPOUND OBSERVATIONS =====")

        if result["exact_count"]:
            print(result["exact_records"].head(15).to_string(index=False))
        else:
            print("No exact parent-compound records found.")

        print("\n===== RELATED COMPOUND OBSERVATIONS =====")

        if result["related_count"]:
            print(result["related_records"].head(10).to_string(index=False))
        else:
            print("No name-related records found.")

        print("\nShowing up to 15 exact and 10 related records.")
