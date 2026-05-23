from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

class LoanApplicationRequest(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the user")
    income: float = Field(..., gt=0, description="Annual income of the applicant")
    credit_score: int = Field(..., ge=300, le=900, description="Credit score (300-900)")
    employment_length: int = Field(..., ge=0, description="Employment length in years (time at current job)")
    existing_loans: float = Field(..., ge=0, description="Total outstanding loans")
    total_debt: float = Field(..., ge=0, description="Total liabilities")
    credit_card_usage: float = Field(..., ge=0, description="Monthly credit card spending")
    loan_amount_requested: float = Field(..., gt=0, description="Requested loan amount")
    loan_tenure: Optional[int] = Field(default=None, ge=1, le=30, description="Requested loan term in years")
    currency: Optional[str] = Field(default="USD", description="Currency type: USD or INR")

class KYCRequest(BaseModel):
    user_id: Optional[str] = None
    aadhaar_number: Optional[str] = None
    pan_number: Optional[str] = None

class KYCResponse(BaseModel):
    kyc_status: str
    message: str

class UserProfile(BaseModel):
    user_id: str
    name: str
    email: str
    phone: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    total_applications: int = 0
    approved_count: int = 0
    rejected_count: int = 0
    review_count: int = 0

class FeatureImpact(BaseModel):
    feature: str
    impact: str

class AgentDecisionResponse(BaseModel):
    risk_score: float = Field(..., description="Probability of default")
    confidence: float = Field(..., description="Agent confidence score")
    decision: str = Field(..., description="Approve, Reject, or Review")
    explanation: str = Field(..., description="Natural language reasoning")
    dti: float = Field(..., description="Calculated Debt-to-Income ratio")
    important_features: List[FeatureImpact] = Field(..., description="Key features and their impacts")

class DownloadReportRequest(BaseModel):
    user_id: str
    income: float
    credit_score: int
    employment_length: int
    existing_loans: float
    total_debt: float
    credit_card_usage: float
    loan_amount_requested: float
    loan_tenure: Optional[int] = None
    currency: Optional[str] = "USD"
    risk_score: float
    confidence: float
    decision: str
    explanation: str
    dti: float
    important_features: List[FeatureImpact]

class LoggedDecision(AgentDecisionResponse):
    user_id: str
    application_data: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)
