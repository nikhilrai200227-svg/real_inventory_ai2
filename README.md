# InventoryPilot AI 📊

**AI-powered inventory intelligence platform** combining demand forecasting, explainable AI, and agentic workflows for smarter inventory management decisions.

## 🎯 Vision

InventoryPilot AI helps businesses optimize inventory levels, prevent stockouts, reduce holding costs, and make data-driven decisions through:
- **Machine Learning** demand forecasting (Random Forest, XGBoost, LightGBM, CatBoost)
- **Explainable AI** with SHAP to understand forecast drivers
- **Generative AI** powered by Gemini for business insights
- **Multi-agent workflows** for collaborative analysis
- **Interactive dashboard** for real-time monitoring
- **Production API** for system integration

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose (optional, for containerized deployment)
- Google Gemini API key (for AI assistant features)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/inventorypilot.git
cd inventorypilot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### Running the Dashboard

```bash
# Generate sample data
python generate_sample_data.py

# Start Streamlit dashboard
streamlit run dashboard.py
```

The dashboard will be available at `http://localhost:8501`

### Running the Backend API

```bash
# In another terminal
python -m uvicorn backend:app --reload --host 0.0.0.0 --port 8000
```

API documentation available at `http://localhost:8000/docs`

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Backend: http://localhost:8000
# Dashboard: http://localhost:8501
# API Docs: http://localhost:8000/docs
```

## 📁 Project Structure

```
inventorypilot/
├── dashboard.py              # Streamlit interactive dashboard
├── backend.py                # FastAPI REST API
├── forecaster.py             # Machine learning forecasting engine
├── explainer.py              # SHAP-based explanations
├── agents.py                 # LangGraph multi-agent system
├── generate_sample_data.py   # Sample data generator
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker image config
├── docker-compose.yml        # Container orchestration
├── .env.example              # Environment template
├── data/                     # Data storage (created on first run)
├── models/                   # Trained models (created on first run)
├── reports/                  # Generated reports (created on first run)
└── README.md                 # This file
```

## 🎨 Features Overview

### 1. 📈 Demand Forecasting
Multiple machine learning models automatically trained and compared:
- **Random Forest**: Robust ensemble approach
- **XGBoost**: Gradient boosting excellence
- **LightGBM**: Fast, memory-efficient gradient boosting
- **CatBoost**: Categorical feature handling

Models are evaluated on MAE, RMSE, and R² metrics. Best performer automatically selected.

```python
forecaster = DemandForecaster()
X_train, X_test, y_train, y_test, df = forecaster.prepare_data(df)
results = forecaster.train_models(X_train, X_test, y_train, y_test)
forecast = forecaster.forecast(df, days_ahead=30)
```

### 2. 💡 Explainable AI
SHAP-powered explanations answer "why" behind predictions:
- Global feature importance
- Prediction-level explanations
- Business-friendly interpretations

```python
explainer = ExplainablePredictor(model, X_train, feature_names)
shap_values = explainer.explain_prediction(X_instance)
business_insights = explainer.explain_business_impact(prediction, shap_values, X_instance)
```

### 3. 🤖 AI Business Assistant
Gemini-powered conversational AI answers business questions:
- "Which products should we reorder?"
- "What's driving demand spikes?"
- "How should we adjust safety stock?"

Uses structured prompts to generate actionable recommendations.

### 4. 🏗️ Multi-Agent Workflow
LangGraph-based agent collaboration:
```
User Question
    ↓
[Forecast Agent] → Analyzes demand patterns
    ↓
[Explanation Agent] → Interprets key drivers
    ↓
[Recommendation Agent] → Generates actions
    ↓
[Executive Agent] → Synthesizes summary
    ↓
Executive Report
```

### 5. 📊 Interactive Dashboard
Streamlit-powered interface with:
- Real-time sales trends
- Product performance metrics
- Demand forecasts with model comparison
- SHAP feature importance visualizations
- AI assistant chat
- Executive report generation
- Data upload capability

### 6. 🔌 REST API
FastAPI backend exposing:
- `/api/v1/predict` - Generate forecasts
- `/api/v1/explain` - Get prediction explanations
- `/api/v1/analytics` - Inventory health metrics
- `/api/v1/query` - AI assistant queries
- `/api/v1/upload` - Custom data upload

Example:
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{"product_id": "PROD_001", "days_ahead": 30}'
```

### 7. 📋 Executive Reports
Automated report generation with:
- Sales summaries
- Demand forecasts
- Risk assessments
- Recommended actions
- Business KPIs

## 📊 Data Format

Expected CSV format:
```csv
date,product_id,product_name,sales,inventory_level,reorder_point,category
2023-01-01,PROD_001,Product 1,150,450,150,Electronics
2023-01-02,PROD_001,Product 1,165,440,150,Electronics
...
```

Required columns: `date`, `product_id`, `sales`, `inventory_level`
Optional: `product_name`, `reorder_point`, `category`

## 🔧 Configuration

Edit `.env` file:

```env
# Gemini API Configuration
GOOGLE_API_KEY=your_key_here

# Backend Settings
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Streamlit Settings
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Paths
DATA_PATH=./data
MODELS_PATH=./models
REPORTS_PATH=./reports

# Forecast Settings
FORECAST_DAYS=30
TEST_SIZE=0.2
RANDOM_STATE=42
```

## 📈 Workflow Examples

### Example 1: Generate Forecast
```python
from forecaster import DemandForecaster
from generate_sample_data import generate_sample_data

# Load data
df = generate_sample_data()

# Train forecaster
forecaster = DemandForecaster()
X_train, X_test, y_train, y_test, df_proc = forecaster.prepare_data(df)
results = forecaster.train_models(X_train, X_test, y_train, y_test)

# Generate forecast
forecast = forecaster.forecast(df, days_ahead=30)
print(f"Next 30 days forecast: {forecast}")

# Save model
forecaster.save_model()
```

### Example 2: Explain Predictions
```python
from explainer import ExplainablePredictor
import numpy as np

# Create explainer
explainer = ExplainablePredictor(
    forecaster.best_model,
    X_train,
    forecaster.feature_names
)

# Get business-friendly explanation
explanation = explainer.explain_business_impact(
    prediction=150,
    shap_values=None,
    X_instance=X_test[0:1],
    historical_mean=X_train.mean()
)

print(explanation['business_summary'])
```

### Example 3: Ask AI Assistant
```python
from agents import InventoryAgents

agents = InventoryAgents(api_key="your_gemini_key")

forecast_data = {
    'avg_daily_demand': 150,
    'peak_demand': 200,
    'trend': 'upward',
    'confidence': 0.92
}

result = agents.process_query(
    "Which products should we reorder?",
    forecast_data
)

print(result['executive_report'])
```

### Example 4: Call REST API
```bash
# Start backend
python -m uvicorn backend:app --host 0.0.0.0 --port 8000

# Make prediction request
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{"product_id": "PROD_001", "days_ahead": 30}' | jq

# Get analytics
curl "http://localhost:8000/api/v1/analytics" | jq

# Ask AI assistant
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "Which products are at risk of stockout?"}' | jq
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_forecaster.py -v

# Run with coverage
pytest --cov=. --cov-report=html
```

## 📦 Deployment

### Local Development
```bash
# Terminal 1: Backend
python -m uvicorn backend:app --reload

# Terminal 2: Dashboard
streamlit run dashboard.py
```

### Docker Deployment
```bash
# Build images
docker-compose build

# Start services
docker-compose up

# Stop services
docker-compose down
```

### Cloud Deployment (Heroku, AWS, etc.)

See `DEPLOYMENT.md` for detailed cloud deployment instructions.

## 🔑 API Authentication

For production, implement API key authentication:

```python
# backend.py - Add to FastAPI app
from fastapi.security import APIKeyHeader
from fastapi import Depends, HTTPException

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
```

## 🐛 Troubleshooting

**Issue: Gemini API errors**
- Verify `GOOGLE_API_KEY` in `.env`
- Check API key has required permissions
- App works offline (uses mock responses)

**Issue: Out of memory with large datasets**
- Reduce batch size in forecaster
- Use sample of data for testing
- Enable disk caching in LightGBM/CatBoost

**Issue: Slow model training**
- Reduce number of features
- Use smaller `n_estimators`
- Enable parallel processing (`n_jobs=-1`)

**Issue: Dashboard not loading**
- Clear Streamlit cache: `streamlit cache clear`
- Check port 8501 is available
- Verify data files in `./data` directory

## 📚 Technology Stack

**ML & Data Processing**
- Pandas, NumPy, Scikit-learn
- XGBoost, LightGBM, CatBoost
- Optuna (hyperparameter optimization)

**Explainability**
- SHAP, LIME

**Frontend**
- Streamlit
- Plotly (interactive visualizations)

**Backend**
- FastAPI, Pydantic
- Uvicorn (ASGI server)

**AI & Agents**
- LangChain, LangGraph
- Google Generative AI (Gemini)

**Deployment**
- Docker, Docker Compose

## 🚀 Future Enhancements

- [ ] Real-time data streaming
- [ ] Advanced anomaly detection
- [ ] Supply chain optimization
- [ ] Supplier integration APIs
- [ ] Mobile app (React Native)
- [ ] Advanced scheduling (Celery)
- [ ] Multi-user authentication
- [ ] Data warehouse integration (BigQuery, Snowflake)
- [ ] Advanced visualization (3D demand surfaces)
- [ ] Custom model training interface
- [ ] A/B testing framework
- [ ] Automated hyperparameter tuning

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📧 Support & Contact

- 📧 Email: support@inventorypilot.ai
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions
- 🌐 Website: https://inventorypilot.ai

## 🙏 Acknowledgments

Built with modern AI/ML stack:
- Scikit-learn & XGBoost communities
- LangChain & LangGraph frameworks
- Streamlit for intuitive dashboards
- Google Generative AI team

---

**InventoryPilot AI v1.0.0** | Made with ❤️ for smarter inventory management
