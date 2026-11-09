
import json
import csv
from pathlib import Path
from collections import Counter

MOF_DIR = Path(
    "/Users/dishanair/Downloads/bulk-dl-mofdb-version-dc8a0295db"
)

PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_DIR / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "mof_database_index.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

fields = [
    "mof_name",
    "mof_id",
    "database",
    "lcd_A",
    "pld_A",
    "surface_area_m2g",
    "surface_area_m2cm3",
    "void_fraction",
    "elements",
    "adsorbates",
    "isotherm_count",
    "temperatures_K",
    "pressure_min_bar",
    "pressure_max_bar",
    "doi_references",
]

files = sorted(MOF_DIR.rglob("*.json"))

processed = 0
failed = 0
adsorbate_counts = Counter()

with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()

    for number, file_path in enumerate(files, start=1):
        try:
            with file_path.open(encoding="utf-8") as f:
                data = json.load(f)

            isotherms = data.get("isotherms") or []

            adsorbates = sorted({
                item.get("name", "Unknown")
                for item in (data.get("adsorbates") or [])
            })

            for name in adsorbates:
                adsorbate_counts[name] += 1

            temperatures = sorted({
                iso.get("temperature")
                for iso in isotherms
                if isinstance(iso.get("temperature"), (int, float))
            })

            pressures = [
                point.get("pressure")
                for iso in isotherms
                for point in (iso.get("isotherm_data") or [])
                if isinstance(point.get("pressure"), (int, float))
            ]

            dois = sorted({
                iso.get("DOI")
                for iso in isotherms
                if iso.get("DOI")
            })

            row = {
                "mof_name": data.get("name", ""),
                "mof_id": data.get("id", ""),
                "database": data.get("database", ""),
                "lcd_A": data.get("lcd", ""),
                "pld_A": data.get("pld", ""),
                "surface_area_m2g": data.get("surface_area_m2g", ""),
                "surface_area_m2cm3": data.get("surface_area_m2cm3", ""),
                "void_fraction": data.get("void_fraction", ""),
                "elements": "; ".join(
                    json.dumps(item, ensure_ascii=False) if isinstance(item, dict)
                    else str(item)
                    for item in (data.get("elements") or [])
                ),
                "adsorbates": "; ".join(adsorbates),
                "isotherm_count": len(isotherms),
                "temperatures_K": "; ".join(map(str, temperatures)),
                "pressure_min_bar": min(pressures) if pressures else "",
                "pressure_max_bar": max(pressures) if pressures else "",
                "doi_references": "; ".join(dois),
            }

            writer.writerow(row)
            processed += 1

        except Exception as error:
            failed += 1
            if failed <= 5:
                print(f"\nFAILED FILE: {file_path}")
                print(f"ERROR TYPE: {type(error).__name__}")
                print(f"ERROR DETAILS: {error}")

        if number % 10000 == 0:
            print(f"Processed {number:,} / {len(files):,} files")

print("\nMOF INDEX BUILD COMPLETE")
print("Total JSON files:", len(files))
print("Successfully indexed:", processed)
print("Failed files:", failed)
print("Output:", OUTPUT_FILE)

print("\nAdsorbate categories:")
for name, count in adsorbate_counts.most_common():
    print(f"{name}: {count:,}")
