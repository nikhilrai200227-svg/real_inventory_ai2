# InventoryPilot AI - Quick Start Guide 🚀

## 30-Second Setup

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/inventorypilot.git
cd inventorypilot

# 2. Run setup script
bash setup.sh

# 3. Choose option 1 (Dashboard) or 2 (API) or 3 (Both)
```

## Running the Dashboard

```bash
# Terminal 1: Start the dashboard
streamlit run dashboard.py
```

Visit `http://localhost:8501` in your browser

### Dashboard Features:
- 📊 **Overview** - Sales trends and product performance
- 🔮 **Forecasting** - Generate demand forecasts with model comparison
- 💡 **Explanations** - Understand what drives predictions (SHAP)
- 🤖 **AI Assistant** - Ask business questions
- 📋 **Reports** - Generate executive reports
- ⚙️ **Settings** - Configure the app

## Running the Backend API

```bash
# Terminal 2: Start the API
python -m uvicorn backend:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/docs` for interactive API documentation

### API Endpoints:
- `POST /api/v1/predict` - Generate forecast
- `POST /api/v1/explain` - Get prediction explanation
- `GET /api/v1/analytics` - Get inventory analytics
- `POST /api/v1/query` - Ask AI assistant
- `POST /api/v1/upload` - Upload custom data

## Using Docker

```bash
# Start both services with Docker Compose
docker-compose up --build

# Services will be available at:
# - Dashboard: http://localhost:8501
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

## API Examples

### Get Demand Forecast
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "PROD_001",
    "days_ahead": 30
  }' | jq
```

### Get Inventory Analytics
```bash
curl "http://localhost:8000/api/v1/analytics" | jq
```

### Ask AI Assistant
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Which products should we reorder?"
  }' | jq
```

### Upload Custom Data
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@your_data.csv"
```

## Python API Integration

```python
import requests

# Initialize API client
API_URL = "http://localhost:8000/api/v1"

# Get forecast
response = requests.post(f"{API_URL}/predict", json={
    "product_id": "PROD_001",
    "days_ahead": 30
})
forecast = response.json()
print(f"Forecast: {forecast['forecast']}")

# Get analytics
response = requests.get(f"{API_URL}/analytics")
analytics = response.json()
print(f"Total Products: {analytics['total_products']}")

# Ask AI assistant
response = requests.post(f"{API_URL}/query", json={
    "question": "Which products are at risk?"
})
result = response.json()
print(f"Report: {result['executive_report']}")
```

## Testing the API

```bash
# Test all endpoints
python test_api.py
```

This runs comprehensive tests on all API endpoints and displays results.

## Data Format

Upload CSV with these columns:
```csv
date,product_id,product_name,sales,inventory_level,reorder_point,category
2023-01-01,PROD_001,Product 1,150,450,150,Electronics
2023-01-02,PROD_001,Product 1,165,440,150,Electronics
```

Required: `date`, `product_id`, `sales`, `inventory_level`
Optional: `product_name`, `reorder_point`, `category`

## Environment Configuration

Edit `.env` file:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
STREAMLIT_SERVER_PORT=8501
FORECAST_DAYS=30
```

Get your Gemini API key from: https://ai.google.dev

## Common Tasks

### Generate New Sample Data
```bash
python generate_sample_data.py
```

### Train Forecasting Model
```python
from forecaster import DemandForecaster
from generate_sample_data import generate_sample_data

df = generate_sample_data()
forecaster = DemandForecaster()
X_train, X_test, y_train, y_test, _ = forecaster.prepare_data(df)
results = forecaster.train_models(X_train, X_test, y_train, y_test)
forecast = forecaster.forecast(df, days_ahead=30)
```

### Get SHAP Explanations
```python
from explainer import ExplainablePredictor

explainer = ExplainablePredictor(model, X_train, feature_names)
shap_values = explainer.explain_prediction(X_test[0:1])
explanation = explainer.explain_business_impact(prediction, shap_values, X_test[0:1])
print(explanation['business_summary'])
```

### Query AI Assistant
```python
from agents import InventoryAgents

agents = InventoryAgents(api_key="your_gemini_key")
result = agents.process_query(
    "Which products need reordering?",
    {"avg_daily_demand": 150, "trend": "upward"}
)
print(result['executive_report'])
```

## Troubleshooting

**Port Already in Use**
```bash
# Find and kill process on port 8501
lsof -ti:8501 | xargs kill -9

# Or use different port
streamlit run dashboard.py --server.port=8502
```

**Dependencies Issues**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Or use fresh virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**API Not Responding**
```bash
# Check if API is running
curl http://localhost:8000/health

# Start API explicitly
python -m uvicorn backend:app --reload
```

**Dashboard Won't Load**
```bash
# Clear Streamlit cache
streamlit cache clear

# Check if port 8501 is available
lsof -ti:8501

# Run with verbose logging
streamlit run dashboard.py --logger.level=debug
```

## Next Steps

1. **Explore the Dashboard** - Generate forecasts and see explanations
2. **Use the API** - Integrate into your own applications
3. **Upload Your Data** - Replace sample data with real inventory data
4. **Configure Gemini** - Add your API key for AI features
5. **Deploy to Production** - Use Docker for cloud deployment

## Documentation

- **Full README**: See `README.md`
- **API Docs**: http://localhost:8000/docs (when running)
- **Code Examples**: See `test_api.py`

## Support

- 🐛 Report bugs on GitHub Issues
- 💬 Ask questions in Discussions
- 📧 Email: support@inventorypilot.ai

---

**InventoryPilot AI v1.0.0** | Made with ❤️ for smarter inventory
