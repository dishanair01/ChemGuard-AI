from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "data" / "processed" / "environmental_measurements.csv"
OUTPUT_DIR = ROOT / "data" / "processed" / "environmental_analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CONCENTRATION_UNITS = {
    "µg/L",
    "mg/L",
    "ng/L",
    "g/L",
    "mg/kg",
    "mg/kg dry-weight",
    "mg/kg moist-weight",
    "µg/kg dry-weight",
}
DIMENSIONLESS_UNITS = {"[-]"}
PLACEHOLDERS = {-9999, -9.999}


def load_data():
    df = pd.read_csv(INPUT_FILE, low_memory=False)

    required = [
        "Name of Analyte", "Matrix", "Sampling Country", "Statistics",
        "Detection", "MEC standardized", "Unit standard",
        "Literature Citation",
    ]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df


def classify_measurements(df):
    df = df.copy()

    df["MEC standardized"] = pd.to_numeric(
        df["MEC standardized"], errors="coerce"
    )

    for column in ["Statistics", "Detection", "Unit standard"]:
        df[column] = df[column].astype("string").str.strip()

    stats = df["Statistics"].str.casefold()
    detection = df["Detection"].str.casefold()

    placeholder = df["MEC standardized"].isin(PLACEHOLDERS)
    missing_value = df["MEC standardized"].isna() | placeholder

    below_detection = detection.str.contains("below detection", na=False)
    smaller_than = stats.eq("smaller than").fillna(False)
    larger_than = stats.eq("larger than").fillna(False)

    df["Measurement Status"] = "exact"
    df.loc[smaller_than | larger_than | below_detection, "Measurement Status"] = "censored"
    # Missing numeric values/placeholders take precedence over censoring labels.
    df.loc[missing_value, "Measurement Status"] = "missing"

    zero_positive = (
        detection.eq("positive detection")
        & df["MEC standardized"].eq(0)
        & ~missing_value
    )
    df["Review Flag"] = ""
    df.loc[zero_positive, "Review Flag"] = (
        "Positive detection with zero MEC - verify source"
    )

    df["Censoring Type"] = ""
    df.loc[below_detection | smaller_than, "Censoring Type"] = "upper-bound / below-detection"
    df.loc[larger_than, "Censoring Type"] = "lower-bound"
    return df


def split_measurements(df):
    units = df["Unit standard"].astype("string").str.strip()
    concentration_mask = units.isin(CONCENTRATION_UNITS)
    dimensionless_mask = units.isin(DIMENSIONLESS_UNITS)

    concentration = df[concentration_mask].copy()
    dimensionless = df[dimensionless_mask].copy()
    other_units = df[~(concentration_mask | dimensionless_mask)].copy()

    exact = concentration[concentration["Measurement Status"] == "exact"].copy()
    censored = concentration[concentration["Measurement Status"] == "censored"].copy()
    missing = concentration[concentration["Measurement Status"] == "missing"].copy()

    return concentration, exact, censored, missing, dimensionless, other_units


def create_matrix_summary(exact):
    group_columns = [
        "Name of Analyte", "Matrix", "Unit standard", "Statistics"
    ]
    summary = (
        exact.groupby(group_columns, dropna=False)
        .agg(
            observation_count=("MEC standardized", "count"),
            minimum=("MEC standardized", "min"),
            median=("MEC standardized", "median"),
            maximum=("MEC standardized", "max"),
            mean=("MEC standardized", "mean"),
            countries=("Sampling Country", "nunique"),
        )
        .reset_index()
    )
    summary.to_csv(OUTPUT_DIR / "exact_matrix_summary.csv", index=False)


def create_country_summary(exact):
    group_columns = [
        "Name of Analyte", "Sampling Country", "Matrix",
        "Unit standard", "Statistics",
    ]
    summary = (
        exact.groupby(group_columns, dropna=False)
        .agg(
            observation_count=("MEC standardized", "count"),
            median=("MEC standardized", "median"),
            maximum=("MEC standardized", "max"),
        )
        .reset_index()
    )
    summary.to_csv(OUTPUT_DIR / "exact_country_summary.csv", index=False)


def create_record_report(df, filename, columns=None):
    if columns is not None:
        available = [column for column in columns if column in df.columns]
        df = df[available]
    df.to_csv(OUTPUT_DIR / filename, index=False)


def create_quality_report(df, concentration, exact, censored, missing,
                          dimensionless, other_units):
    report = {
        "total_records": len(df),
        "concentration_records": len(concentration),
        "exact_measurements": len(exact),
        "censored_measurements": len(censored),
        "missing_measurements": len(missing),
        "dimensionless_records": len(dimensionless),
        "other_or_unclassified_unit_records": len(other_units),
        "unique_compounds": df["Name of Analyte"].nunique(),
        "unique_matrices": df["Matrix"].nunique(),
        "unique_countries": df["Sampling Country"].nunique(),
        "unique_literature_sources": df["Literature Citation"].nunique(),
        "positive_detection_zero_mec_review_records": int(
            (df["Review Flag"] != "").sum()
        ),
        "lower_bound_records_in_concentration_subset": int(
            censored["Censoring Type"].eq("lower-bound").sum()
        ),
    }

    pd.DataFrame(report.items(), columns=["Metric", "Value"]).to_csv(
        OUTPUT_DIR / "measurement_quality_report.csv", index=False
    )
    return report


def main():
    print("\\n====================================")
    print("       CHEMGUARD AI")
    print("   MEASUREMENT CLASSIFICATION")
    print("====================================\\n")

    df = load_data()
    print(f"Loaded records: {len(df):,}")

    classified = classify_measurements(df)
    (
        concentration, exact, censored, missing,
        dimensionless, other_units,
    ) = split_measurements(classified)

    create_matrix_summary(exact)
    create_country_summary(exact)

    report_columns = [
        "ID", "Name of Analyte", "Matrix", "Sampling Country",
        "Statistics", "Detection", "MEC original", "Unit original",
        "MEC standardized", "Unit standard", "LoD Limit of Detection",
        "Unit LoD standardized", "Literature Citation",
        "Measurement Status", "Censoring Type", "Review Flag",
    ]

    create_record_report(censored, "censored_measurements.csv", report_columns)
    create_record_report(missing, "missing_measurements.csv")
    create_record_report(
        classified[classified["Review Flag"] != ""],
        "records_requiring_review.csv",
        report_columns,
    )
    create_record_report(dimensionless, "dimensionless_measurements.csv")
    create_record_report(other_units, "other_or_unclassified_units.csv")

    report = create_quality_report(
        classified, concentration, exact, censored, missing,
        dimensionless, other_units,
    )

    print("\\nMeasurement classification:")
    for key, value in report.items():
        print(f"{key}: {value:,}")

    print("\\nReports saved to:")
    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()
