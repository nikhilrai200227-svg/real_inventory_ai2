"""
Machine Learning Forecasting Engine
Handles demand prediction using multiple models
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostRegressor
from sklearn.ensemble import RandomForestRegressor
import joblib
import os
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

class DemandForecaster:
    """Multi-model demand forecasting engine"""
    
    def __init__(self, models_dir='./models'):
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)
        self.models = {}
        self.scaler = MinMaxScaler()
        self.best_model = None
        self.best_model_name = None
        self.feature_names = None
        
    def create_features(self, df, lag_days=7):
        """Create lagged features for time series forecasting"""
        df = df.sort_values('date').reset_index(drop=True)
        
        features_list = []
        for lag in range(1, lag_days + 1):
            df[f'sales_lag_{lag}'] = df['sales'].shift(lag)
            features_list.append(f'sales_lag_{lag}')
        
        # Rolling averages
        df['sales_ma_7'] = df['sales'].rolling(window=7, min_periods=1).mean()
        df['sales_ma_14'] = df['sales'].rolling(window=14, min_periods=1).mean()
        features_list.extend(['sales_ma_7', 'sales_ma_14'])
        
        # Temporal features
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_month'] = df['date'].dt.day
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        features_list.extend(['day_of_week', 'day_of_month', 'month', 'quarter', 'is_weekend'])
        
        # Drop rows with NaN from lag features
        df = df.dropna()
        
        self.feature_names = features_list
        return df, features_list
    
    def prepare_data(self, df, product_id=None, test_size=0.2):
        """Prepare data for modeling"""
        if product_id:
            df = df[df['product_id'] == product_id].copy()
        
        df, features = self.create_features(df)
        
        X = df[features].values
        y = df['sales'].values
        
        # Scale features
        X = self.scaler.fit_transform(X)
        
        split_idx = int(len(X) * (1 - test_size))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        return X_train, X_test, y_train, y_test, df
    
    def train_models(self, X_train, X_test, y_train, y_test):
        """Train multiple models and select the best"""
        models_config = {
            'RandomForest': RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                random_state=42,
                n_jobs=-1
            ),
            'XGBoost': xgb.XGBRegressor(
                n_estimators=100,
                max_depth=7,
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1
            ),
            'LightGBM': lgb.LGBMRegressor(
                n_estimators=100,
                max_depth=7,
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1,
                verbose=-1
            ),
            'CatBoost': CatBoostRegressor(
                iterations=100,
                depth=7,
                learning_rate=0.1,
                random_state=42,
                verbose=0
            )
        }
        
        results = {}
        for name, model in models_config.items():
            try:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                
                mae = mean_absolute_error(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                r2 = r2_score(y_test, y_pred)
                
                results[name] = {
                    'model': model,
                    'mae': mae,
                    'rmse': rmse,
                    'r2': r2
                }
                
                self.models[name] = model
                
            except Exception as e:
                print(f"Error training {name}: {str(e)}")
        
        # Select best model based on RMSE
        self.best_model_name = min(results, key=lambda x: results[x]['rmse'])
        self.best_model = results[self.best_model_name]['model']
        
        return results
    
    def forecast(self, df, product_id=None, days_ahead=30):
        """Generate forecast for future days"""
        if product_id:
            df = df[df['product_id'] == product_id].copy()
        
        df, features = self.create_features(df)
        
        # Use last row as starting point
        last_row = df.iloc[-1].copy()
        
        forecasts = []
        current_data = df.copy()
        
        for day in range(days_ahead):
            # Prepare features for prediction
            X_pred = current_data[features].iloc[-1:].values
            X_pred = self.scaler.transform(X_pred)
            
            # Predict
            pred = self.best_model.predict(X_pred)[0]
            pred = max(0, pred)  # Ensure non-negative
            
            forecasts.append(pred)
            
            # Update data for next prediction
            new_date = last_row['date'] + timedelta(days=day+1)
            new_row = {
                'date': new_date,
                'sales': pred,
                'day_of_week': new_date.dayofweek,
                'day_of_month': new_date.day,
                'month': new_date.month,
                'quarter': new_date.quarter,
                'is_weekend': 1 if new_date.dayofweek >= 5 else 0
            }
            
            # Add lag features
            for lag in range(1, 8):
                if lag <= len(forecasts):
                    new_row[f'sales_lag_{lag}'] = forecasts[-lag]
                else:
                    new_row[f'sales_lag_{lag}'] = last_row[f'sales_lag_{lag}']
            
            new_row['sales_ma_7'] = np.mean(forecasts[-7:]) if len(forecasts) >= 7 else last_row['sales_ma_7']
            new_row['sales_ma_14'] = np.mean(forecasts[-14:]) if len(forecasts) >= 14 else last_row['sales_ma_14']
            
            new_df = pd.DataFrame([new_row])
            current_data = pd.concat([current_data, new_df], ignore_index=True)
        
        return np.array(forecasts)
    
    def save_model(self, product_id=None):
        """Save trained model"""
        suffix = f"_{product_id}" if product_id else ""
        model_path = os.path.join(self.models_dir, f'best_model{suffix}.pkl')
        joblib.dump(self.best_model, model_path)
        return model_path
    
    def load_model(self, product_id=None):
        """Load trained model"""
        suffix = f"_{product_id}" if product_id else ""
        model_path = os.path.join(self.models_dir, f'best_model{suffix}.pkl')
        if os.path.exists(model_path):
            self.best_model = joblib.load(model_path)
            return True
        return False

if __name__ == "__main__":
    from generate_sample_data import generate_sample_data
    
    # Generate sample data
    df = generate_sample_data()
    
    # Train forecaster
    forecaster = DemandForecaster()
    X_train, X_test, y_train, y_test, df_processed = forecaster.prepare_data(df)
    results = forecaster.train_models(X_train, X_test, y_train, y_test)
    
    print("\n📊 Model Performance Comparison:")
    print("=" * 50)
    for name, metrics in results.items():
        print(f"\n{name}:")
        print(f"  MAE:  {metrics['mae']:.2f}")
        print(f"  RMSE: {metrics['rmse']:.2f}")
        print(f"  R²:   {metrics['r2']:.4f}")
    
    print(f"\n✓ Best Model: {forecaster.best_model_name}")
    
    # Generate forecast
    forecast = forecaster.forecast(df, days_ahead=30)
    print(f"\n📈 30-day forecast (first 5 days): {forecast[:5].round(2)}")
    
    # Save model
    forecaster.save_model()
    print("✓ Model saved successfully")
