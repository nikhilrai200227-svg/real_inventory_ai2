FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p ./data ./models ./reports

# Expose ports
EXPOSE 8000 8501

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_HEADLESS=true

# Default command (can be overridden)
CMD ["sh", "-c", "python generate_sample_data.py && streamlit run dashboard.py --server.port=8501 --server.address=0.0.0.0"]
