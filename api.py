# Create a separate API file: api.py
# Run with: uvicorn api:app --reload

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import json
from typing import Optional

app = FastAPI(title="Smart EDA API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class DataRequest(BaseModel):
    data: list
    columns: Optional[list] = None

class AnalysisRequest(BaseModel):
    data: list
    analysis_type: str  # 'eda', 'correlation', 'statistics'

@app.get("/")
def root():
    return {"message": "Smart EDA API", "version": "1.0.0"}

@app.post("/analyze")
def analyze_data(request: AnalysisRequest):
    try:
        df = pd.DataFrame(request.data)
        
        if request.analysis_type == "eda":
            # Return EDA results
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
            return {
                "correlation_matrix": numeric.corr().to_dict()
            }
        
        elif request.analysis_type == "statistics":
            return {
                "statistics": df.describe().to_dict()
            }
        
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis type")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict")
def predict(request: dict):
    # Placeholder for ML prediction
    return {
        "message": "Predictions endpoint",
        "data": request
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

# To run: uvicorn api:app --reload
