"""
Explainable AI (XAI) Module
Provides SHAP-based explanations for model predictions
"""
import shap
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
import os
from datetime import datetime

class ExplainablePredictor:
    """Generate SHAP explanations for predictions"""
    
    def __init__(self, model, X_train, feature_names):
        self.model = model
        self.X_train = X_train
        self.feature_names = feature_names
        self.explainer = None
        self.shap_values = None
        
    def create_explainer(self):
        """Initialize SHAP explainer"""
        try:
            # Use TreeExplainer for tree-based models
            if hasattr(self.model, 'get_booster'):  # XGBoost
                self.explainer = shap.TreeExplainer(self.model)
            elif hasattr(self.model, 'booster_'):  # LightGBM/CatBoost
                self.explainer = shap.TreeExplainer(self.model)
            elif hasattr(self.model, 'estimators_'):  # RandomForest
                self.explainer = shap.TreeExplainer(self.model)
            else:
                self.explainer = shap.KernelExplainer(self.model.predict, 
                                                      shap.sample(self.X_train, 100))
            return True
        except Exception as e:
            print(f"Error creating explainer: {e}")
            return False
    
    def explain_prediction(self, X_instance):
        """Generate explanation for a single prediction"""
        if self.explainer is None:
            self.create_explainer()
        
        shap_values = self.explainer.shap_values(X_instance)
        
        # Handle list output (for some models)
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        
        return shap_values
    
    def get_feature_importance(self):
        """Get global feature importance from SHAP values"""
        if self.explainer is None:
            self.create_explainer()
        
        shap_values = self.explainer.shap_values(self.X_train[:100])
        
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        
        importance = np.abs(shap_values).mean(axis=0)
        
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        return importance_df
    
    def explain_business_impact(self, prediction, shap_values, X_instance, 
                                historical_mean=None):
        """Convert SHAP values to business-friendly explanations"""
        
        if historical_mean is None:
            historical_mean = self.X_train.mean()
        
        explanation = {
            'prediction': float(prediction),
            'top_drivers': [],
            'business_summary': ''
        }
        
        # Sort by absolute SHAP value
        feature_impacts = list(zip(self.feature_names, shap_values[0]))
        feature_impacts = sorted(feature_impacts, key=lambda x: abs(x[1]), reverse=True)
        
        # Get top 3 drivers
        for i, (feature, shap_val) in enumerate(feature_impacts[:3]):
            direction = "increasing" if shap_val > 0 else "decreasing"
            impact = abs(shap_val)
            
            explanation['top_drivers'].append({
                'rank': i + 1,
                'feature': feature,
                'impact': float(impact),
                'direction': direction,
                'interpretation': f"{feature.replace('_', ' ').title()} is {direction} demand"
            })
        
        # Business summary
        top_driver = explanation['top_drivers'][0]
        explanation['business_summary'] = (
            f"Expected demand is {prediction:.0f} units. "
            f"The primary driver is {top_driver['feature']} "
            f"({top_driver['direction']} demand by {top_driver['impact']:.1f} units). "
            f"Action: Monitor {top_driver['feature']} trends closely."
        )
        
        return explanation
    
    def generate_report(self, X_instance, prediction, output_path=None):
        """Generate full explainability report"""
        shap_values = self.explain_prediction(X_instance)
        explanation = self.explain_business_impact(prediction, shap_values, X_instance)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'prediction': prediction,
            'confidence': 'High' if prediction > 0 else 'Low',
            'explanation': explanation,
            'model_info': {
                'type': type(self.model).__name__,
                'features_used': len(self.feature_names),
                'explainer_type': type(self.explainer).__name__
            }
        }
        
        return report

def create_shap_visualizations(explainer, X_test, feature_names, output_dir='./reports'):
    """Create and save SHAP visualizations"""
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        shap_values = explainer.shap_values(X_test[:100])
        
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        
        # Feature importance plot
        plt.figure(figsize=(10, 6))
        importance = np.abs(shap_values).mean(axis=0)
        indices = np.argsort(importance)[-10:]
        plt.barh(range(len(indices)), importance[indices])
        plt.yticks(range(len(indices)), [feature_names[i] for i in indices])
        plt.xlabel('Mean |SHAP value|')
        plt.title('Feature Importance (Top 10)')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'feature_importance.png'), dpi=150)
        plt.close()
        
        print(f"✓ SHAP visualizations saved to {output_dir}")
        
    except Exception as e:
        print(f"Error creating SHAP visualizations: {e}")

if __name__ == "__main__":
    print("Explainable AI module loaded successfully")
