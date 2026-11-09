
import pandas as pd
from pathlib import Path


# ============================================================
# CHEMGUARD AI
# Environmental Pharmaceutical Data Analysis
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "environmental_measurements.csv"
)


# Supported measurement units
CONCENTRATION_UNITS = [
    "µg/L",
    "mg/kg",
    "mg/kg dry-weight",
    "mg/kg moist-weight"
]

DIMENSIONLESS_UNITS = ["[-]"]

# Known placeholder values in MEC standardized.
INVALID_PLACEHOLDERS = [-9999, -9.999]

# Columns required for the analysis
REQUIRED_COLUMNS = [
    "Name of Analyte",
    "Matrix",
    "Sampling Country",
    "Unit standard",
    "Statistics",
    "MEC standardized",
    "Sampling Period Start",
    "Sampling Period End"
]


# ============================================================
# LOAD DATA
# ============================================================

def load_environmental_data():

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Environmental dataset not found:\n{DATA_FILE}"
        )

    df = pd.read_csv(
        DATA_FILE,
        low_memory=False
    )

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Required columns are missing from the dataset:\n"
            + ", ".join(missing_columns)
        )

    return df


# ============================================================
# ANALYZE ENVIRONMENTAL DATA
# ============================================================

def analyze_environmental_data(compound_name):

    df = load_environmental_data()

    compound_name = compound_name.strip()

    if not compound_name:
        print("Please enter a valid compound name.")
        return

    # Normalize analyte names for exact matching
    analyte_names = (
        df["Name of Analyte"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.casefold()
    )

    records = df[
        analyte_names == compound_name.casefold()
    ].copy()

    if records.empty:
        print(
            f"\nNo exact environmental records found "
            f"for '{compound_name}'."
        )
        return

    print("\n" + "=" * 65)
    print("             CHEMGUARD AI")
    print("       ENVIRONMENTAL DATA ANALYSIS")
    print("=" * 65)

    print("\nCOMPOUND:", compound_name)
    print("TOTAL OBSERVATIONS:", len(records))

    # --------------------------------------------------------
    # 1. PREPARE DATA
    # --------------------------------------------------------

    records["MEC standardized"] = pd.to_numeric(
        records["MEC standardized"],
        errors="coerce"
    )

    records["Unit standard"] = (
        records["Unit standard"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )

    records["Matrix"] = (
        records["Matrix"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )

    records["Sampling Country"] = (
        records["Sampling Country"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )

    records["Statistics"] = (
        records["Statistics"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )

    # Count known placeholder values before excluding them
    placeholder_count = int(
        records["MEC standardized"]
        .isin(INVALID_PLACEHOLDERS)
        .sum()
    )

    # Exclude placeholders from numerical calculations
    records["MEC standardized"] = records[
        "MEC standardized"
    ].mask(
        records["MEC standardized"].isin(
            INVALID_PLACEHOLDERS
        )
    )

    print("\n" + "-" * 65)
    print("1. DATA PREPARATION")
    print("-" * 65)

    print(
        "Placeholder values excluded from calculations:",
        placeholder_count
    )

    print(
        "Missing or non-numeric MEC values:",
        int(records["MEC standardized"].isna().sum())
    )

    # --------------------------------------------------------
    # 2. MATRIX DISTRIBUTION
    # --------------------------------------------------------

    print("\n" + "-" * 65)
    print("2. ENVIRONMENTAL MATRIX DISTRIBUTION")
    print("-" * 65)

    print(
        records["Matrix"]
        .value_counts()
        .to_string()
    )

    # --------------------------------------------------------
    # 3. COUNTRY DISTRIBUTION
    # --------------------------------------------------------

    print("\n" + "-" * 65)
    print("3. COUNTRY DISTRIBUTION")
    print("-" * 65)

    print(
        records["Sampling Country"]
        .value_counts()
        .head(20)
        .to_string()
    )

    # --------------------------------------------------------
    # 4. MEASUREMENT UNIT DISTRIBUTION
    # --------------------------------------------------------

    print("\n" + "-" * 65)
    print("4. MEASUREMENT UNIT DISTRIBUTION")
    print("-" * 65)

    print(
        records["Unit standard"]
        .value_counts()
        .to_string()
    )

    # --------------------------------------------------------
    # 5. STATISTICAL MEASUREMENT TYPES
    # --------------------------------------------------------

    print("\n" + "-" * 65)
    print("5. STATISTICAL MEASUREMENT TYPES")
    print("-" * 65)

    print(
        records["Statistics"]
        .value_counts()
        .to_string()
    )

    # --------------------------------------------------------
    # 6. CONCENTRATION ANALYSIS
    # --------------------------------------------------------

    print("\n" + "-" * 65)
    print("6. CONCENTRATION ANALYSIS")
    print("-" * 65)

    concentration_records = records[
        records["Unit standard"].isin(
            CONCENTRATION_UNITS
        )
    ].copy()

    valid_concentrations = concentration_records.dropna(
        subset=["MEC standardized"]
    ).copy()

    if valid_concentrations.empty:

        print("No valid concentration measurements found.")

    else:

        grouped = valid_concentrations.groupby(
            [
                "Matrix",
                "Unit standard",
                "Statistics"
            ],
            dropna=False
        )["MEC standardized"]

        summary = grouped.agg(
            count="count",
            minimum="min",
            median="median",
            maximum="max"
        )

        print(
            "\nConcentration summaries"
            "\n(Grouped by matrix, unit and statistic type):\n"
        )

        print(summary.to_string())

    # --------------------------------------------------------
    # 7. DIMENSIONLESS MEASUREMENT ANALYSIS
    # --------------------------------------------------------

    print("\n" + "-" * 65)
    print("7. DIMENSIONLESS MEASUREMENT ANALYSIS")
    print("-" * 65)

    dimensionless_records = records[
        records["Unit standard"].isin(
            DIMENSIONLESS_UNITS
        )
    ].copy()

    valid_dimensionless = dimensionless_records.dropna(
        subset=["MEC standardized"]
    )

    if valid_dimensionless.empty:

        print("No dimensionless measurements found.")

    else:

        dimensionless_summary = (
            valid_dimensionless
            .groupby(
                ["Matrix", "Statistics"],
                dropna=False
            )["MEC standardized"]
            .agg(
                count="count",
                minimum="min",
                median="median",
                maximum="max"
            )
        )

        print(
            "\nDimensionless measurements "
            "(not treated as concentrations):\n"
        )

        print(dimensionless_summary.to_string())

    # --------------------------------------------------------
    # 8. UNUSUAL HIGH CONCENTRATION VALUES
    # --------------------------------------------------------

    print("\n" + "-" * 65)
    print("8. UNUSUAL HIGH MEASUREMENTS")
    print("-" * 65)

    print(
        "The following are the largest recorded values "
        "within each concentration unit."
    )

    if valid_concentrations.empty:

        print("No valid concentration measurements to inspect.")

    else:

        for unit in CONCENTRATION_UNITS:

            unit_records = valid_concentrations[
                valid_concentrations["Unit standard"] == unit
            ].copy()

            if unit_records.empty:
                continue

            print(f"\nUNIT: {unit}")

            columns_to_show = [
                column
                for column in [
                    "ID",
                    "Name of Analyte",
                    "Matrix",
                    "Statistics",
                    "MEC standardized",
                    "Sampling Country",
                    "Literature Citation"
                ]
                if column in unit_records.columns
            ]

            largest_records = unit_records.nlargest(
                5,
                "MEC standardized"
            )

            print(
                largest_records[columns_to_show]
                .to_string(index=False)
            )

    # --------------------------------------------------------
    # 9. DATA QUALITY
    # --------------------------------------------------------

    print("\n" + "-" * 65)
    print("9. DATA QUALITY REPORT")
    print("-" * 65)

    print(
        "Exact duplicate rows:",
        int(records.duplicated().sum())
    )

    print(
        "\nMissing values by column:\n"
    )

    print(
        records.isnull()
        .sum()
        .to_string()
    )

    # --------------------------------------------------------
    # 10. SAMPLING YEAR ANALYSIS
    # --------------------------------------------------------

    print("\n" + "-" * 65)
    print("10. SAMPLING YEAR ANALYSIS")
    print("-" * 65)

    for column in [
        "Sampling Period Start",
        "Sampling Period End"
    ]:

        years = pd.to_numeric(
            records[column],
            errors="coerce"
        )

        # Exclude missing and invalid year values
        years = years[
            (years >= 1900)
            & (years <= 2026)
        ]

        if years.empty:

            print(column + ": No valid years found")

        else:

            print(
                column + ": "
                + f"{int(years.min())} - "
                + f"{int(years.max())}"
            )

    # --------------------------------------------------------
    # 11. FINAL ANALYSIS SUMMARY
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("             ANALYSIS COMPLETED")
    print("=" * 65)

    print("Compound:", compound_name)
    print("Total observations:", len(records))
    print(
        "Concentration observations:",
        len(valid_concentrations)
    )
    print(
        "Dimensionless observations:",
        len(valid_dimensionless)
    )
    print(
        "Placeholder values excluded:",
        placeholder_count
    )

    print("\nNote:")
    print(
        "These records represent database observations, "
        "not necessarily independent studies."
    )

    print(
        "Measurements with different units, matrices "
        "and statistic types are kept separate."
    )

    print(
        "Unusual values are reported for investigation "
        "and are not automatically discarded."
    )

    print("\nCHEMGUARD AI ANALYSIS FINISHED.")
    print("=" * 65)


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    try:

        compound = input(
            "\nEnter pharmaceutical compound: "
        ).strip()

        analyze_environmental_data(compound)

    except FileNotFoundError as error:

        print("\nFILE ERROR:")
        print(error)

    except ValueError as error:

        print("\nDATA VALIDATION ERROR:")
        print(error)

    except Exception as error:

        print("\nUNEXPECTED ERROR:")
        print(type(error).__name__, "-", error)
