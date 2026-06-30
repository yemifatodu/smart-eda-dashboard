# Run with: uvicorn api:app --reload
#
# Set an API key before running:
#   export SMART_EDA_API_KEY="some-long-random-value"

import os
import logging

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, conlist
import pandas as pd
from typing import Optional

logger = logging.getLogger("smart_eda_api")

app = FastAPI(title="Smart EDA API", version="1.0.0")

# Lock CORS down to an explicit allowlist instead of "*". Set this env var
# to a comma-separated list of the origins that are actually allowed to
# call this API (e.g. your deployed frontend's domain).
ALLOWED_ORIGINS = [
    o.strip() for o in os.environ.get("SMART_EDA_ALLOWED_ORIGINS", "").split(",") if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # empty by default -> no cross-origin browser calls allowed
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

API_KEY = os.environ.get("SMART_EDA_API_KEY")
MAX_ROWS = 50_000  # guard against payload-driven memory exhaustion


def require_api_key(x_api_key: Optional[str] = Header(default=None)):
    if not API_KEY:
        # Fail closed: if no key is configured, refuse all requests rather
        # than silently running unauthenticated.
        raise HTTPException(status_code=503, detail="API is not configured")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True


class AnalysisRequest(BaseModel):
    data: conlist(dict, max_length=MAX_ROWS)
    analysis_type: str  # 'eda', 'correlation', 'statistics'


@app.get("/")
def root():
    return {"message": "Smart EDA API", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/analyze")
def analyze_data(request: AnalysisRequest, authorized: bool = Depends(require_api_key)):
    try:
        df = pd.DataFrame(request.data)

        if request.analysis_type == "eda":
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            return {
                "shape": df.shape,
                "columns": df.columns.tolist(),
                "numeric_columns": numeric_cols,
                "summary": df.describe().to_dict(),
                "missing": df.isnull().sum().to_dict()
            }

        elif request.analysis_type == "correlation":
            numeric = df.select_dtypes(include=['number'])
            return {"correlation_matrix": numeric.corr().to_dict()}

        elif request.analysis_type == "statistics":
            return {"statistics": df.describe().to_dict()}

        else:
            raise HTTPException(status_code=400, detail="Invalid analysis type")

    except HTTPException:
        raise
    except Exception:
        # Log the real error server-side, but never leak internals to the client.
        logger.exception("analyze_data failed")
        raise HTTPException(status_code=500, detail="Internal error processing request")


@app.post("/predict")
def predict(request: dict, authorized: bool = Depends(require_api_key)):
    # NOTE: this endpoint is still a placeholder. Wire it up to
    # utils/model_trainer.py before relying on it for anything real —
    # right now it just echoes the request back.
    raise HTTPException(status_code=501, detail="Prediction endpoint not yet implemented")
