import os
import re
from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any
from PyPDF2 import PdfReader
import io

from api.routes import router
from api.schemas import LoanApplicationRequest, AgentDecisionResponse, FeatureImpact
from services.credit_bureau_service import credit_bureau_service
from tools.risk_model import predict_risk
from tools.explainability import explain_prediction
from tools.decision import decision_engine
from database import insert_loan_application
from utils.db import connect_to_db, close_db_connection
from utils.logger import get_logger
from config import settings
import uvicorn

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up application...")
    await connect_to_db()
    yield
    # Shutdown
    logger.info("Shutting down application...")
    await close_db_connection()

app = FastAPI(
    title="Autonomous Credit Risk Agent API",
    description="An AI agent backend for analyzing loan risk.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.post("/verify-income")
async def verify_income(
    claimed_income: str = Form(...),
    document: UploadFile = File(...)
):
    """
    Payslip Document Verification endpoint for fraud detection.
    Accepts claimed income and a PDF document, extracts text from PDF,
    and checks if the claimed income appears in the document.
    """
    try:
        logger.info(f"Starting income verification for claimed income: {claimed_income}")
        
        # Validate file type
        if not document.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported for payslip verification"
            )
        
        # Read PDF content
        pdf_content = await document.read()
        pdf_file = io.BytesIO(pdf_content)
        
        # Extract text from PDF
        try:
            pdf_reader = PdfReader(pdf_file)
            extracted_text = ""
            for page in pdf_reader.pages:
                extracted_text += page.extract_text()
            
            logger.info(f"Successfully extracted {len(extracted_text)} characters from PDF")
        except Exception as pdf_error:
            logger.error(f"Failed to read PDF: {pdf_error}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to read PDF document: {str(pdf_error)}"
            )
        
        # Normalize both claimed income and extracted text
        # Remove commas, spaces, dollar signs, and convert to lowercase
        def normalize_text(text: str) -> str:
            return re.sub(r'[\s,$]', '', text.lower())
        
        normalized_claimed_income = normalize_text(claimed_income)
        normalized_extracted_text = normalize_text(extracted_text)
        
        # Check if claimed income exists in the PDF text
        income_found = normalized_claimed_income in normalized_extracted_text
        
        verification_result = {
            "verified": income_found,
            "payslip_filename": document.filename,
            "claimed_income": claimed_income,
            "verification_timestamp": datetime.utcnow().isoformat()
        }
        
        if income_found:
            logger.info(f"Income verification PASSED: {claimed_income} found in document")
            return {
                "status": "success",
                "fraud_flag": False,
                "message": "Income verification successful. The claimed income matches the payslip document.",
                "verification_data": verification_result
            }
        else:
            logger.warning(f"Income verification FAILED: {claimed_income} NOT found in document")
            return {
                "status": "success",
                "fraud_flag": True,
                "message": "Fraud Alert: The claimed income does not match the payslip document. Please verify your income information.",
                "verification_data": verification_result
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unhandled error in income verification: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during income verification: {str(e)}"
        )


@app.post("/analyze-loan-complete", response_model=AgentDecisionResponse)
async def analyze_loan_complete(
    application: LoanApplicationRequest,
    background_tasks: BackgroundTasks
):
    """
    Complete loan analysis endpoint that integrates:
    1. Mock Credit Bureau API for credit velocity data
    2. AI Risk Model for probability prediction
    3. SHAP explainability for feature attributions
    4. Decision Engine for final authorization
    5. MongoDB for persistent storage
    """
    try:
        logger.info(f"Starting loan analysis for user: {application.user_id}")
        
        # STEP 1: Call Mock Credit Bureau API
        logger.info("Step 1: Fetching credit bureau data...")
        credit_bureau_data = await credit_bureau_service.get_credit_data(
            user_id=application.user_id,
            full_name=""
        )
        
        credit_velocity = credit_bureau_data.get("credit_score", application.credit_score)
        debt_index = credit_bureau_data.get("debt_index", application.dti)
        
        logger.info(
            f"Credit Bureau Response - Score: {credit_velocity}, "
            f"Debt Index: {debt_index}, Bureau: {credit_bureau_data.get('bureau_name')}"
        )
        
        final_credit_score = credit_velocity
        final_dti = debt_index
        
        # STEP 2: AI Risk Prediction
        logger.info("Step 2: Running AI risk prediction...")
        risk_probability, confidence_score = predict_risk(
            income=application.income,
            credit_score=final_credit_score,
            dti=final_dti,
            employment_length=application.employment_length
        )
        
        logger.info(
            f"AI Prediction - Risk Probability: {risk_probability:.4f}, "
            f"Confidence: {confidence_score:.4f}"
        )
        
        # STEP 3: SHAP Explainability
        logger.info("Step 3: Generating SHAP feature attributions...")
        shap_features = explain_prediction(
            income=application.income,
            credit_score=final_credit_score,
            dti=final_dti,
            employment_length=application.employment_length
        )
        
        important_features = [
            FeatureImpact(feature=item["feature"], impact=item["impact"])
            for item in shap_features
        ]
        
        logger.info(f"SHAP Analysis - Top feature: {shap_features[0]['feature']}")
        
        # STEP 4: Decision Engine
        logger.info("Step 4: Running decision engine...")
        final_decision, decision_reasoning = decision_engine(
            probability=risk_probability,
            credit_score=final_credit_score,
            dti=final_dti,
            employment_length=application.employment_length
        )
        
        logger.info(f"Decision Engine - Final Decision: {final_decision}")
        
        # STEP 5: Prepare Complete Record for MongoDB
        complete_record: Dict[str, Any] = {
            "applicant_id": application.user_id,
            "user_id": application.user_id,
            "income": application.income,
            "credit_score_input": application.credit_score,
            "dti_input": application.dti,
            "employment_length": application.employment_length,
            "currency": application.currency,
            
            "credit_bureau_data": {
                "credit_velocity": credit_velocity,
                "debt_index": debt_index,
                "credit_history_months": credit_bureau_data.get("credit_history_months"),
                "total_accounts": credit_bureau_data.get("total_accounts"),
                "delinquent_accounts": credit_bureau_data.get("delinquent_accounts"),
                "credit_utilization": credit_bureau_data.get("credit_utilization"),
                "payment_history_score": credit_bureau_data.get("payment_history_score"),
                "bureau_name": credit_bureau_data.get("bureau_name"),
                "api_success": credit_bureau_data.get("success", False)
            },
            
            "ai_analysis": {
                "risk_probability": risk_probability,
                "confidence_score": confidence_score,
                "model_version": "v1.0",
                "final_credit_score_used": final_credit_score,
                "final_dti_used": final_dti
            },
            
            "shap_telemetry": [
                {"feature": f.feature, "impact": f.impact}
                for f in important_features
            ],
            
            "decision": {
                "authorization": final_decision,
                "reasoning": decision_reasoning,
                "timestamp": datetime.utcnow()
            },
            
            "status": final_decision.lower(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # STEP 6: Save to MongoDB (Background Task)
        async def save_to_database():
            try:
                document_id = await insert_loan_application(complete_record)
                logger.info(f"Successfully saved loan analysis to MongoDB with ID: {document_id}")
            except Exception as db_error:
                logger.error(f"Failed to save to MongoDB: {db_error}")
        
        background_tasks.add_task(save_to_database)
        
        # STEP 7: Format Response for Frontend
        response = AgentDecisionResponse(
            risk_score=risk_probability,
            confidence=confidence_score,
            decision=final_decision,
            explanation=decision_reasoning,
            important_features=important_features
        )
        
        logger.info(
            f"Loan analysis completed for user {application.user_id}: "
            f"{final_decision} (Risk: {risk_probability:.2%}, Confidence: {confidence_score:.2%})"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unhandled error in loan analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during loan analysis: {str(e)}"
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
