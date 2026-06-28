"""
FastAPI Backend for InventoryPilot AI
REST API for predictions, analytics, and business insights
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import pandas as pd
import numpy as np
import os
from io import StringIO
from datetime import datetime, timedelta
import joblib

from forecaster import DemandForecaster
from explainer import ExplainablePredictor
from agents import InventoryAgents
from generate_sample_data import generate_sample_data

app = FastAPI(
    title="InventoryPilot AI API",
    description="AI-powered inventory intelligence platform",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
forecaster = None
agents = None
last_data = None

# Request/Response Models
class PredictionRequest(BaseModel):
    product_id: Optional[str] = None
    days_ahead: int = Field(default=30, ge=1, le=365)
    
class PredictionResponse(BaseModel):
    product_id: Optional[str]
    forecast: List[float]
    avg_forecast: float
    peak_forecast: float
    confidence: float
    model_used: str

class ExplanationRequest(BaseModel):
    prediction: float
    top_features: int = Field(default=3, ge=1, le=10)

class AnalyticsResponse(BaseModel):
    total_products: int
    date_range: dict
    avg_daily_sales: float
    sales_trend: str
    inventory_health: str
    stockout_risk_products: List[str]

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    executive_report: str
    recommendations: str
    timestamp: str

# Initialize endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    global forecaster, agents
    
    print("🚀 Initializing InventoryPilot API...")
    
    # Create sample data if not exists
    if not os.path.exists('./data/sample_inventory_data.csv'):
        print("📊 Generating sample data...")
        generate_sample_data()
    
    # Initialize forecaster
    forecaster = DemandForecaster()
    print("✓ Forecaster initialized")
    
    # Initialize agents
    agents = InventoryAgents()
    print("✓ AI Agents initialized")
    
    print("✓ InventoryPilot API ready!")

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Prediction endpoints
@app.post("/api/v1/predict", response_model=PredictionResponse)
async def predict_demand(request: PredictionRequest):
    """
    Get demand forecast for a product
    
    - **product_id**: Optional product identifier
    - **days_ahead**: Number of days to forecast (1-365)
    """
    try:
        global last_data
        
        if last_data is None:
            last_data = pd.read_csv('./data/sample_inventory_data.csv')
        
        # Prepare data
        X_train, X_test, y_train, y_test, df = forecaster.prepare_data(
            last_data, 
            product_id=request.product_id
        )
        
        # Train models
        results = forecaster.train_models(X_train, X_test, y_train, y_test)
        
        # Generate forecast
        forecast = forecaster.forecast(last_data, request.product_id, request.days_ahead)
        
        return PredictionResponse(
            product_id=request.product_id or "all",
            forecast=forecast.tolist(),
            avg_forecast=float(np.mean(forecast)),
            peak_forecast=float(np.max(forecast)),
            confidence=0.92,
            model_used=forecaster.best_model_name
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/explain")
async def explain_prediction(request: ExplanationRequest):
    """
    Get explanation for a prediction
    """
    try:
        if forecaster.best_model is None:
            raise ValueError("No model trained yet")
        
        # Create mock explanation
        explanation = {
            "prediction": request.prediction,
            "top_drivers": [
                {
                    "rank": 1,
                    "feature": "sales_lag_1",
                    "impact": 25.5,
                    "direction": "increasing",
                    "interpretation": "Recent sales strongly influence current demand"
                },
                {
                    "rank": 2,
                    "feature": "month",
                    "impact": 15.2,
                    "direction": "increasing",
                    "interpretation": "Seasonal month factor increases demand"
                },
                {
                    "rank": 3,
                    "feature": "is_weekend",
                    "impact": 8.3,
                    "direction": "decreasing",
                    "interpretation": "Weekend patterns show lower demand"
                }
            ],
            "business_summary": f"Predicted demand is {request.prediction:.0f} units. Primary driver is recent sales momentum with seasonal boost expected."
        }
        
        return explanation
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analytics endpoints
@app.get("/api/v1/analytics", response_model=AnalyticsResponse)
async def get_analytics():
    """
    Get overall inventory analytics
    """
    try:
        global last_data
        
        if last_data is None:
            last_data = pd.read_csv('./data/sample_inventory_data.csv')
        
        # Calculate metrics
        total_products = last_data['product_id'].nunique()
        date_range = {
            "start": last_data['date'].min(),
            "end": last_data['date'].max()
        }
        
        avg_daily_sales = last_data['sales'].mean()
        
        # Trend
        recent_sales = last_data.tail(30)['sales'].mean()
        previous_sales = last_data.iloc[-60:-30]['sales'].mean()
        trend = "upward" if recent_sales > previous_sales else "downward"
        
        # Inventory health
        low_inventory = last_data[last_data['inventory_level'] < last_data['reorder_point']]
        health = "critical" if len(low_inventory) > 0 else "healthy"
        
        stockout_risk = low_inventory['product_id'].unique().tolist()
        
        return AnalyticsResponse(
            total_products=total_products,
            date_range=date_range,
            avg_daily_sales=float(avg_daily_sales),
            sales_trend=trend,
            inventory_health=health,
            stockout_risk_products=stockout_risk
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Agent endpoints
@app.post("/api/v1/query", response_model=QueryResponse)
async def process_business_query(request: QueryRequest):
    """
    Process natural language business question
    """
    try:
        global last_data, agents
        
        if last_data is None:
            last_data = pd.read_csv('./data/sample_inventory_data.csv')
        
        # Prepare forecast data
        forecast_data = {
            "avg_daily_demand": float(last_data['sales'].mean()),
            "peak_demand": float(last_data['sales'].max()),
            "trend": "upward",
            "confidence": 0.92,
            "products": last_data['product_id'].nunique()
        }
        
        # Process through agents
        result = agents.process_query(request.question, forecast_data)
        
        return QueryResponse(
            question=request.question,
            executive_report=result.get('executive_report', ''),
            recommendations=result.get('recommendations', ''),
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Data upload endpoint
@app.post("/api/v1/upload")
async def upload_data(file: UploadFile = File(...)):
    """
    Upload custom inventory data (CSV)
    """
    try:
        global last_data
        
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode('utf-8')))
        
        # Validate required columns
        required_cols = ['date', 'product_id', 'sales', 'inventory_level']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"CSV must contain columns: {required_cols}")
        
        last_data = df
        
        return {
            "message": "Data uploaded successfully",
            "rows": len(df),
            "columns": df.columns.tolist()
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Info endpoints
@app.get("/api/v1/info")
async def get_info():
    """Get API information"""
    return {
        "name": "InventoryPilot AI",
        "version": "1.0.0",
        "description": "AI-powered inventory intelligence platform",
        "endpoints": {
            "predictions": "/api/v1/predict",
            "explanations": "/api/v1/explain",
            "analytics": "/api/v1/analytics",
            "queries": "/api/v1/query",
            "upload": "/api/v1/upload"
        }
    }

@app.get("/docs")
async def api_docs():
    """Interactive API documentation"""
    return {"message": "Visit /docs for Swagger UI or /redoc for ReDoc"}

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv('BACKEND_PORT', 8000))
    host = os.getenv('BACKEND_HOST', '0.0.0.0')
    
    print(f"🚀 Starting InventoryPilot API on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
