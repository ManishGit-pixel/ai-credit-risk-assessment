from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import numpy as np
import pickle
import os

# Create dummy data
np.random.seed(42)
n_samples = 1000

# Features: income, credit_score, employment_length, total_debt, credit_card_usage, loan_amount_requested, existing_loans
income = np.random.uniform(20000, 200000, n_samples)
credit_score = np.random.randint(300, 850, n_samples)
employment_length = np.random.randint(0, 40, n_samples)
total_debt = np.random.uniform(0, 100000, n_samples)
credit_card_usage = np.random.uniform(0, 10000, n_samples)
loan_amount_requested = np.random.uniform(1000, 50000, n_samples)
existing_loans = np.random.uniform(0, 50000, n_samples)

# Simplified logic to generate targets (1 = Default, 0 = Paid)
dti = total_debt / income
# Clamp DTI
dti_clamped = np.clip(dti, 0, 1)

risk_score = (850 - credit_score)/550 + 2*dti_clamped - income/400000 + loan_amount_requested/100000
risk_score += (existing_loans / 50000) * 0.2
risk_score += (credit_card_usage / 10000) * 0.1

probabilities = 1 / (1 + np.exp(-(risk_score - np.mean(risk_score))))
target = (probabilities > 0.6).astype(int)

df = pd.DataFrame({
    'income': income,
    'credit_score': credit_score,
    'employment_length': employment_length,
    'total_debt': total_debt,
    'credit_card_usage': credit_card_usage,
    'loan_amount_requested': loan_amount_requested,
    'existing_loans': existing_loans
})

# Train model using RandomForest
model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
model.fit(df, target)

# Save model
os.makedirs('models', exist_ok=True)
with open('models/dummy_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Dummy RandomForest model trained and saved to models/dummy_model.pkl")
