import shap
import pandas as pd
from tools.risk_model import get_model

# We create an explainer once model is loaded
_explainer = None

def get_explainer():
    global _explainer
    if _explainer is None:
        model = get_model()
        # TreeExplainer is best for XGBoost
        _explainer = shap.TreeExplainer(model)
    return _explainer

def explain_prediction(
    income: float, 
    credit_score: int, 
    employment_length: int,
    total_debt: float,
    credit_card_usage: float,
    loan_amount_requested: float,
    existing_loans: float
) -> list:
    """
    Use SHAP to explain the model's prediction.
    Returns a list of dictionaries with feature name and its contribution (SHAP value).
    """
    explainer = get_explainer()
    
    df = pd.DataFrame([{
        'income': income,
        'credit_score': credit_score,
        'employment_length': employment_length,
        'total_debt': total_debt,
        'credit_card_usage': credit_card_usage,
        'loan_amount_requested': loan_amount_requested,
        'existing_loans': existing_loans
    }])
    
    shap_values = explainer.shap_values(df)
    
    # Depending on xgboost and shap versions, shap_values might be a list or array
    # Assume binary classification, so we take the values for class 1 if it's a list
    if isinstance(shap_values, list):
        vals = shap_values[1][0]
    elif len(shap_values.shape) == 3: # (samples, features, classes)
        vals = shap_values[0, :, 1]
    else:
        vals = shap_values[0]
        
    feature_names = df.columns.tolist()
    
    explanation = []
    for i, feature in enumerate(feature_names):
        contribution = float(vals[i])
        if contribution < -0.1:
            impact = "High positive impact reducing risk"
        elif contribution < 0:
            impact = "Moderate positive impact reducing risk"
        elif contribution == 0:
            impact = "Neutral impact"
        elif contribution < 0.1:
            impact = "Moderate negative impact increasing risk"
        else:
            impact = "High negative impact increasing risk"
            
        explanation.append({
            "feature": feature,
            "raw_contrib": contribution,
            "impact": impact
        })
        
    # Rank by absolute importance
    explanation.sort(key=lambda x: abs(x["raw_contrib"]), reverse=True)
    
    # Return formatted schema matching FeatureImpact
    return [{"feature": e["feature"], "impact": e["impact"]} for e in explanation]
