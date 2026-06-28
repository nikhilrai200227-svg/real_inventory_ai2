"""
Generate sample inventory data for testing and demonstration
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_sample_data(n_days=365, n_products=10):
    """Generate realistic sample inventory data"""
    np.random.seed(42)
    
    dates = pd.date_range(start='2023-01-01', periods=n_days, freq='D')
    
    data = []
    for product_id in range(1, n_products + 1):
        # Create realistic demand patterns with seasonality and trend
        trend = np.linspace(0, 20, n_days)
        seasonality = 30 * np.sin(np.arange(n_days) * 2 * np.pi / 365)
        noise = np.random.normal(0, 10, n_days)
        
        sales = np.maximum(50 + trend + seasonality + noise, 0).astype(int)
        inventory = np.random.randint(100, 500, n_days)
        
        for i, date in enumerate(dates):
            data.append({
                'date': date,
                'product_id': f'PROD_{product_id:03d}',
                'product_name': f'Product {product_id}',
                'sales': int(sales[i]),
                'inventory_level': int(inventory[i]),
                'reorder_point': 150 + product_id * 10,
                'category': ['Electronics', 'Clothing', 'Food', 'Home'][product_id % 4]
            })
    
    df = pd.DataFrame(data)
    return df

def create_sample_data_file():
    """Create and save sample data file"""
    os.makedirs('./data', exist_ok=True)
    
    df = generate_sample_data(n_days=365, n_products=10)
    df.to_csv('./data/sample_inventory_data.csv', index=False)
    
    print(f"✓ Sample data created: ./data/sample_inventory_data.csv")
    print(f"  Shape: {df.shape}")
    print(f"\nFirst few rows:")
    print(df.head())
    
    return df

if __name__ == "__main__":
    create_sample_data_file()
