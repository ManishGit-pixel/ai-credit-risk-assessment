"""
Pydantic Models for Loan Application
Production-ready schemas with comprehensive validation
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class CurrencyType(str, Enum):
    """Supported currency types"""
    USD = "USD"
    INR = "INR"


class LoanStatus(str, Enum):
    """Loan application status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"


class LoanApplicationCreate(BaseModel):
    """
    Schema for creating a new loan application
    Includes strict validation for all financial fields
    """
    applicant_id: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique identifier for the applicant",
        example="APP-2024-001"
    )
    
    annual_income: float = Field(
        ...,
        gt=0,
        le=10_000_000_000,  # 10 billion max
        description="Annual income in the specified currency",
        example=85000.00
    )
    
    credit_velocity: int = Field(
        ...,
        ge=300,
        le=850,
        description="Credit score (FICO scale: 300-850)",
        example=720
    )
    
    debt_index: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Debt-to-Income ratio (0.0 to 1.0)",
        example=0.35
    )
    
    employment_length: int = Field(
        ...,
        ge=0,
        le=50,
        description="Employment length in years (how long at current job)",
        example=5
    )
    
    loan_tenure: Optional[int] = Field(
        default=None,
        ge=1,
        le=30,
        description="Requested loan tenure/term in years",
        example=15
    )
    
    currency: Optional[CurrencyType] = Field(
        default=CurrencyType.USD,
        description="Currency type for income"
    )
    
    loan_amount_requested: Optional[float] = Field(
        default=None,
        gt=0,
        le=100_000_000,
        description="Requested loan amount"
    )
    
    loan_purpose: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Purpose of the loan"
    )
    
    @field_validator('applicant_id')
    @classmethod
    def validate_applicant_id(cls, v):
        """Validate applicant ID format"""
        if not v or v.isspace():
            raise ValueError('Applicant ID cannot be empty or whitespace')
        
        # Remove leading/trailing whitespace
        v = v.strip()
        
        # Check for valid characters (alphanumeric, hyphens, underscores)
        if not all(c.isalnum() or c in ['-', '_'] for c in v):
            raise ValueError('Applicant ID can only contain alphanumeric characters, hyphens, and underscores')
        
        return v
    
    @field_validator('annual_income')
    @classmethod
    def validate_income(cls, v, info):
        """Validate income based on currency"""
        currency = info.data.get('currency', CurrencyType.USD)
        
        if currency == CurrencyType.USD:
            # Minimum wage check (roughly $15k/year)
            if v < 15000:
                raise ValueError('Annual income must be at least $15,000 USD')
        elif currency == CurrencyType.INR:
            # Minimum wage check (roughly ₹200k/year)
            if v < 200000:
                raise ValueError('Annual income must be at least ₹200,000 INR')
        
        return round(v, 2)
    
    @field_validator('debt_index')
    @classmethod
    def validate_debt_index(cls, v):
        """Validate and round debt index"""
        return round(v, 4)
    
    @field_validator('loan_amount_requested')
    @classmethod
    def validate_loan_amount(cls, v, info):
        """Validate loan amount doesn't exceed reasonable limits"""
        if v is not None:
            annual_income = info.data.get('annual_income', 0)
            if annual_income > 0 and v > annual_income * 10:
                raise ValueError('Loan amount cannot exceed 10x annual income')
        return v
    
    @model_validator(mode='after')
    def validate_financial_ratios(self):
        """Cross-field validation for financial health"""
        debt_index = self.debt_index
        credit_velocity = self.credit_velocity
        
        # High debt with low credit score is a red flag
        if debt_index > 0.6 and credit_velocity < 600:
            # This is allowed but we could add a warning field
            pass
        
        return self
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "applicant_id": "APP-2024-001",
                "annual_income": 85000.00,
                "credit_velocity": 720,
                "debt_index": 0.35,
                "employment_length": 5,
                "loan_tenure": 15,
                "currency": "USD",
                "loan_amount_requested": 250000.00,
                "loan_purpose": "Home purchase"
            }
        }


class LoanApplicationResponse(LoanApplicationCreate):
    """
    Schema for loan application response
    Includes additional fields added by the system
    """
    id: Optional[str] = Field(
        default=None,
        description="MongoDB document ID"
    )
    
    status: LoanStatus = Field(
        default=LoanStatus.PENDING,
        description="Current status of the loan application"
    )
    
    risk_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Calculated risk score (0.0 = low risk, 1.0 = high risk)"
    )
    
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Model confidence in the decision"
    )
    
    decision: Optional[str] = Field(
        default=None,
        description="Final decision: Approve, Reject, or Review"
    )
    
    explanation: Optional[str] = Field(
        default=None,
        description="AI-generated explanation for the decision"
    )
    
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when application was created"
    )
    
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when application was last updated"
    )
    
    processed_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when application was processed"
    )
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "applicant_id": "APP-2024-001",
                "annual_income": 85000.00,
                "credit_velocity": 720,
                "debt_index": 0.35,
                "employment_length": 5,
                "loan_tenure": 15,
                "currency": "USD",
                "loan_amount_requested": 250000.00,
                "loan_purpose": "Home purchase",
                "status": "approved",
                "risk_score": 0.15,
                "confidence": 0.92,
                "decision": "Approve",
                "explanation": "Strong financial profile with good credit history",
                "created_at": "2024-04-06T12:00:00Z",
                "updated_at": "2024-04-06T12:05:00Z",
                "processed_at": "2024-04-06T12:05:00Z"
            }
        }


class LoanApplicationUpdate(BaseModel):
    """
    Schema for updating an existing loan application
    All fields are optional
    """
    status: Optional[LoanStatus] = None
    risk_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    decision: Optional[str] = None
    explanation: Optional[str] = None
    processed_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True


class LoanApplicationList(BaseModel):
    """
    Schema for paginated list of loan applications
    """
    total: int = Field(..., description="Total number of applications")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Number of items per page")
    applications: List[LoanApplicationResponse] = Field(..., description="List of loan applications")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 150,
                "page": 1,
                "page_size": 10,
                "applications": []
            }
        }


class LoanDecisionRequest(BaseModel):
    """
    Schema for requesting a loan decision
    Can include additional context
    """
    application_id: str = Field(..., description="Loan application ID")
    use_credit_bureau: bool = Field(default=True, description="Whether to fetch credit bureau data")
    use_plaid_verification: bool = Field(default=False, description="Whether to use Plaid for income verification")
    
    class Config:
        json_schema_extra = {
            "example": {
                "application_id": "507f1f77bcf86cd799439011",
                "use_credit_bureau": True,
                "use_plaid_verification": False
            }
        }


class ErrorResponse(BaseModel):
    """
    Standard error response schema
    """
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Credit velocity must be between 300 and 850",
                "details": {"field": "credit_velocity", "value": 900},
                "timestamp": "2024-04-06T12:00:00Z"
            }
        }


class HealthCheckResponse(BaseModel):
    """
    Health check response schema
    """
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    database: str = Field(..., description="Database connection status")
    version: str = Field(default="1.0.0", description="API version")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-04-06T12:00:00Z",
                "database": "connected",
                "version": "1.0.0"
            }
        }
