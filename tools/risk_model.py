import pickle
import pandas as pd
import os
from config import settings

# Load model globally to avoid reloading on every request
model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'dummy_model.pkl')
model = None

def get_model():
    global model
    if model is None:
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
        else:
            raise FileNotFoundError(f"Model not found at {model_path}. Please run train_dummy.py first.")
    return model

from typing import Tuple

def predict_risk(
    income: float, 
    credit_score: int, 
    employment_length: int,
    total_debt: float,
    credit_card_usage: float,
    loan_amount_requested: float,
    existing_loans: float
) -> Tuple[float, float]:
    """
    Predict the probability of loan default given user financial features.
    Returns a tuple of (risk_score, confidence_score) clamped to realistic bounds.
    """
    m = get_model()
    
    # Create DataFrame with the exact features model was trained on
    df = pd.DataFrame([{
        'income': income,
        'credit_score': credit_score,
        'employment_length': employment_length,
        'total_debt': total_debt,
        'credit_card_usage': credit_card_usage,
        'loan_amount_requested': loan_amount_requested,
        'existing_loans': existing_loans
    }])
    
    # Predict probability of class 1 (Default)
    probability = float(m.predict_proba(df)[0][1])
    
    # Clamp bounds
    probability = max(0.05, min(0.95, probability))
    
    # Compute an independent confidence metric
    distance_from_uncertainty = abs(probability - 0.5) * 2
    confidence = 0.65 + (distance_from_uncertainty * 0.34)
    
    return probability, confidence
