
from pathlib import Path
import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Make the existing backend modules importable
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent

sys.path.insert(0, str(BACKEND_DIR))

from compound_service import get_compound_profile
from environmental_search import search_environmental_records

app = FastAPI(
    title="ChemGuard AI API",
    description="Pharmaceutical and environmental evidence intelligence",
    version="1.0.0"
)

# Allow the local website to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {
        "status": "running",
        "project": "ChemGuard AI"
    }


@app.get("/api/compound/{compound_name}")
def compound_profile(compound_name: str):
    result = get_compound_profile(compound_name)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@app.get("/api/environment/{compound_name}")
def environmental_evidence(compound_name: str):
    result = search_environmental_records(compound_name)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return {
        "search_term": result["search_term"],
        "exact_count": result["exact_count"],
        "related_count": result["related_count"],
        "exact_records": __import__("json").loads(
            result["exact_records"].to_json(orient="records")
        ),
        "related_records": __import__("json").loads(
            result["related_records"].to_json(orient="records")
        )
    }

import pandas as pd

MOF_INDEX_PATH = PROJECT_DIR / "data" / "processed" / "mof_database_index.csv"

@app.get("/api/mofs")
def search_mofs(
    search: str = "",
    adsorbate: str = "",
    limit: int = 20
):
    if not MOF_INDEX_PATH.exists():
        raise HTTPException(status_code=500, detail="MOF database index not found")

    try:
        limit = max(1, min(limit, 100))
        df = pd.read_csv(MOF_INDEX_PATH).fillna("")

        if search:
            mask = (
                df["mof_name"].astype(str).str.contains(search, case=False, na=False, regex=False)
                | df["mof_id"].astype(str).str.contains(search, case=False, na=False, regex=False)
            )
            df = df[mask]

        if adsorbate:
            df = df[
                df["adsorbates"].astype(str).str.contains(
                    adsorbate, case=False, na=False, regex=False
                )
            ]

        total = len(df)
        results = df.head(limit).to_dict(orient="records")

        return {
            "total_results": total,
            "returned_results": len(results),
            "results": results
        }

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
