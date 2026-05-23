"""
AI Engine Service
Handles ML model predictions and SHAP explanations
"""

import pickle
import numpy as np
import pandas as pd
import shap
from pathlib import Path
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class CreditRiskModel:
    """
    Credit Risk ML Model with SHAP explanations
    """
    
    def __init__(self, model_path: str = "models/dummy_model.pkl"):
        """
        Initialize the credit risk model
        
        Args:
            model_path: Path to the trained model file
        """
        self.model = None
        self.model_path = Path(model_path)
        self.feature_names = ['income', 'credit_score', 'dti', 'employment_length']
        self.explainer = None
        self._load_model()
    
    def _load_model(self):
        """Load the trained model from disk"""
        try:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model not found at {self.model_path}")
            
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            logger.info(f"Model loaded successfully from {self.model_path}")
            
            # Initialize SHAP explainer
            self._initialize_explainer()
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise RuntimeError(f"Model loading failed: {e}")
    
    def _initialize_explainer(self):
        """Initialize SHAP explainer for model interpretability"""
        try:
            # Create a small background dataset for SHAP
            # In production, use a representative sample from training data
            background_data = pd.DataFrame({
                'income': [50000, 75000, 100000, 125000],
                'credit_score': [600, 650, 700, 750],
                'dti': [0.2, 0.3, 0.4, 0.5],
                'employment_length': [2, 5, 8, 10]
            })
            
            # Initialize TreeExplainer for tree-based models
            self.explainer = shap.TreeExplainer(self.model, background_data)
            logger.info("SHAP explainer initialized successfully")
            
        except Exception as e:
            logger.warning(f"Could not initialize SHAP explainer: {e}")
            self.explainer = None
    
    def predict(
        self,
        income: float,
        credit_score: int,
        dti: float,
        employment_length: int
    ) -> Tuple[float, float, List[Dict[str, Any]]]:
        """
        Predict credit risk and generate SHAP explanations
        
        Args:
            income: Annual income
            credit_score: Credit score (300-850)
            dti: Debt-to-income ratio (0-1)
            employment_length: Employment length in years
        
        Returns:
            Tuple of (risk_probability, confidence, shap_values)
            - risk_probability: Probability of default (0-1)
            - confidence: Model confidence (0-1)
            - shap_values: List of feature importance dictionaries
        """
        try:
            # Prepare input data
            input_data = pd.DataFrame({
                'income': [income],
                'credit_score': [credit_score],
                'dti': [dti],
                'employment_length': [employment_length]
            })
            
            logger.info(f"Predicting for: income={income}, credit={credit_score}, dti={dti}, tenure={employment_length}")
            
            # Get prediction probabilities
            probabilities = self.model.predict_proba(input_data)
            
            # Risk probability (probability of class 1 - default)
            risk_probability = float(probabilities[0][1])
            
            # Calculate confidence (distance from 0.5)
            confidence = abs(risk_probability - 0.5) * 2
            confidence = min(max(confidence, 0.0), 1.0)
            
            # Get SHAP values for interpretability
            shap_values = self._get_shap_values(input_data)
            
            logger.info(f"Prediction: risk={risk_probability:.4f}, confidence={confidence:.4f}")
            
            return risk_probability, confidence, shap_values
        
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise RuntimeError(f"Model prediction failed: {e}")
    
    def _get_shap_values(self, input_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Calculate SHAP values for feature importance
        
        Args:
            input_data: Input DataFrame
        
        Returns:
            List of dictionaries with feature names and SHAP values
        """
        try:
            if self.explainer is None:
                logger.warning("SHAP explainer not available, returning empty values")
                return self._get_fallback_shap_values(input_data)
            
            # Calculate SHAP values
            shap_values = self.explainer.shap_values(input_data)
            
            # For binary classification, get values for positive class
            if isinstance(shap_values, list):
                shap_values = shap_values[1]  # Class 1 (default)
            
            # Format SHAP values
            feature_importance = []
            for i, feature_name in enumerate(self.feature_names):
                shap_value = float(shap_values[0][i])
                
                # Determine impact direction and magnitude
                if abs(shap_value) > 0.1:
                    impact = "High positive impact" if shap_value > 0 else "High negative impact"
                elif abs(shap_value) > 0.05:
                    impact = "Moderate positive impact" if shap_value > 0 else "Moderate negative impact"
                else:
                    impact = "Low impact"
                
                feature_importance.append({
                    "feature": feature_name,
                    "shap_value": round(shap_value, 4),
                    "impact": impact,
                    "value": float(input_data[feature_name].iloc[0])
                })
            
            # Sort by absolute SHAP value (most important first)
            feature_importance.sort(key=lambda x: abs(x['shap_value']), reverse=True)
            
            return feature_importance
        
        except Exception as e:
            logger.warning(f"SHAP calculation failed: {e}, using fallback")
            return self._get_fallback_shap_values(input_data)
    
    def _get_fallback_shap_values(self, input_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Fallback SHAP values when explainer is not available
        Uses simple heuristics
        """
        credit_score = input_data['credit_score'].iloc[0]
        dti = input_data['dti'].iloc[0]
        income = input_data['income'].iloc[0]
        employment = input_data['employment_length'].iloc[0]
        
        feature_importance = []
        
        # Credit score impact (higher is better)
        if credit_score > 750:
            impact = "High positive impact"
        elif credit_score > 650:
            impact = "Moderate positive impact"
        elif credit_score < 600:
            impact = "High negative impact"
        else:
            impact = "Moderate negative impact"
        
        feature_importance.append({
            "feature": "credit_score",
            "shap_value": (credit_score - 650) / 200,
            "impact": impact,
            "value": float(credit_score)
        })
        
        # DTI impact (lower is better)
        if dti < 0.3:
            impact = "High positive impact"
        elif dti < 0.4:
            impact = "Moderate positive impact"
        elif dti > 0.5:
            impact = "High negative impact"
        else:
            impact = "Moderate negative impact"
        
        feature_importance.append({
            "feature": "dti",
            "shap_value": -(dti - 0.35) * 2,
            "impact": impact,
            "value": float(dti)
        })
        
        # Income impact (higher is better)
        if income > 100000:
            impact = "High positive impact"
        elif income > 60000:
            impact = "Moderate positive impact"
        else:
            impact = "Low impact"
        
        feature_importance.append({
            "feature": "income",
            "shap_value": (income - 60000) / 100000,
            "impact": impact,
            "value": float(income)
        })
        
        # Employment impact
        if employment > 5:
            impact = "Moderate positive impact"
        elif employment < 2:
            impact = "Moderate negative impact"
        else:
            impact = "Low impact"
        
        feature_importance.append({
            "feature": "employment_length",
            "shap_value": (employment - 3) / 10,
            "impact": impact,
            "value": float(employment)
        })
        
        # Sort by absolute SHAP value
        feature_importance.sort(key=lambda x: abs(x['shap_value']), reverse=True)
        
        return feature_importance


class DecisionEngine:
    """
    Decision Engine for loan authorization
    Converts risk scores to final decisions
    """
    
    def __init__(
        self,
        approve_threshold: float = 0.4,
        reject_threshold: float = 0.7
    ):
        """
        Initialize decision engine
        
        Args:
            approve_threshold: Risk score below this = APPROVE
            reject_threshold: Risk score above this = REJECT
        """
        self.approve_threshold = approve_threshold
        self.reject_threshold = reject_threshold
    
    def make_decision(
        self,
        risk_score: float,
        confidence: float,
        credit_score: int = None
    ) -> Tuple[str, str]:
        """
        Make final loan decision based on risk score
        
        Args:
            risk_score: Risk probability (0-1)
            confidence: Model confidence (0-1)
            credit_score: Optional credit score for additional logic
        
        Returns:
            Tuple of (decision, explanation)
            - decision: "APPROVE", "REJECT", or "MANUAL_REVIEW"
            - explanation: Human-readable explanation
        """
        # Low confidence always goes to manual review
        if confidence < 0.6:
            return "MANUAL_REVIEW", "Low model confidence requires manual review"
        
        # Risk-based decision
        if risk_score < self.approve_threshold:
            decision = "APPROVE"
            explanation = self._generate_approval_explanation(risk_score, credit_score)
        
        elif risk_score > self.reject_threshold:
            decision = "REJECT"
            explanation = self._generate_rejection_explanation(risk_score, credit_score)
        
        else:
            decision = "MANUAL_REVIEW"
            explanation = self._generate_review_explanation(risk_score, credit_score)
        
        logger.info(f"Decision: {decision} (risk={risk_score:.4f}, confidence={confidence:.4f})")
        
        return decision, explanation
    
    def _generate_approval_explanation(self, risk_score: float, credit_score: int = None) -> str:
        """Generate explanation for approval"""
        explanations = [
            f"Low risk score of {risk_score:.1%} indicates strong repayment capability.",
            "Applicant demonstrates excellent financial health and creditworthiness.",
            "All key financial indicators are within acceptable ranges for approval."
        ]
        
        if credit_score and credit_score > 750:
            explanations.append("Exceptional credit score further supports approval.")
        
        return " ".join(explanations[:2])
    
    def _generate_rejection_explanation(self, risk_score: float, credit_score: int = None) -> str:
        """Generate explanation for rejection"""
        explanations = [
            f"High risk score of {risk_score:.1%} indicates elevated default probability.",
            "Financial indicators suggest significant repayment risk.",
            "Current financial profile does not meet minimum lending criteria."
        ]
        
        if credit_score and credit_score < 600:
            explanations.append("Low credit score is a primary concern.")
        
        return " ".join(explanations[:2])
    
    def _generate_review_explanation(self, risk_score: float, credit_score: int = None) -> str:
        """Generate explanation for manual review"""
        return (
            f"Risk score of {risk_score:.1%} falls in the borderline range. "
            "Manual review recommended to assess additional factors and context "
            "before making final decision."
        )


# Global instances
credit_risk_model = CreditRiskModel()
decision_engine = DecisionEngine()
