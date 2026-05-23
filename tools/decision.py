from config import settings
from typing import Tuple

def generate_comprehensive_reasoning(decision: str, credit_score: int, dti: float, employment_length: int) -> str:
    positives = []
    negatives = []
    
    if credit_score > 700:
        positives.append("a strong credit score")
    elif credit_score < 600:
        negatives.append("a sub-optimal credit score")
        
    if dti < 0.3:
        positives.append("a low debt-to-income ratio")
    elif dti > 0.5:
        negatives.append("a high debt burden")
        
    if employment_length >= 3:
        positives.append("stable employment history")
    elif employment_length < 1:
        negatives.append("limited employment duration")
        
    if decision == "Approve":
        risk_level = "low risk"
        action_phrase = "an approval decision"
    elif decision == "Reject":
        risk_level = "high risk"
        action_phrase = "a rejection"
    else:
        risk_level = "moderate risk"
        action_phrase = "a requirement for manual review"
        
    if positives and not negatives:
        pos_str = f"{', '.join(positives[:-1])}{' and ' + positives[-1] if len(positives) > 1 else positives[0]}"
        reasons_str = f"due to {pos_str}"
        impact = "These factors indicate good financial discipline and strong repayment capacity"
    elif negatives and not positives:
        neg_str = f"{', '.join(negatives[:-1])}{' and ' + negatives[-1] if len(negatives) > 1 else negatives[0]}"
        reasons_str = f"due to {neg_str}"
        impact = "These factors suggest financial vulnerability and increased default likelihood"
    elif positives and negatives:
        pos_str = f"{', '.join(positives[:-1])}{' and ' + positives[-1] if len(positives) > 1 else positives[0]}"
        neg_str = f"{', '.join(negatives[:-1])}{' and ' + negatives[-1] if len(negatives) > 1 else negatives[0]}"
        reasons_str = f"due to a mix of factors: while demonstrating {pos_str}, the applicant also exhibits {neg_str}"
        impact = "This combination of indicators creates uncertainty regarding absolute repayment reliability"
    else:
        reasons_str = "based on standard baseline financial indicators"
        impact = "These baseline metrics require standard policy evaluation"
        
    return f"The applicant is classified as {risk_level} {reasons_str}. {impact}, leading to {action_phrase}."

def decision_engine(probability: float, credit_score: int, dti: float, employment_length: int) -> Tuple[str, str]:
    """
    Make a loan decision (Approve, Review, Reject) based on the predicted probability of default.
    Using configured dynamic thresholds and computed DTI.
    Returns (decision, rule_based_reasoning).
    """
    if probability < settings.THRESHOLD_APPROVE:
        decision = "Approve"
    elif probability >= settings.THRESHOLD_REJECT:
        decision = "Reject"
    else:
        decision = "Review"
        
    reasoning = generate_comprehensive_reasoning(decision, credit_score, dti, employment_length)
    return decision, reasoning
