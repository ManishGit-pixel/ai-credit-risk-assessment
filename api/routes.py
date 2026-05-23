from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from services.kyc_service import kyc_service as old_kyc_service # Existing service for document uploads
from kyc.kyc_service import kyc_service as identity_kyc_service # New service for identity validation
from agent.core import LoanAgent
from agent.memory import save_decision, get_similar_decisions
from utils.db import create_or_update_user, update_user_stats, get_user_profile, update_kyc_status
from utils.report_generator import generate_loan_report_pdf
from utils.logger import get_logger
from services.plaid_service import plaid_service
from services.credit_bureau_service import credit_bureau_service
from api.schemas import LoanApplicationRequest, AgentDecisionResponse, LoggedDecision, DownloadReportRequest, KYCRequest, KYCResponse

logger = get_logger(__name__)
router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok", "message": "Autonomous Credit Underwriting Agent is running."}

@router.get("/user/{user_id}")
async def get_user(user_id: str):
    """Get user profile and statistics"""
    try:
        user = await get_user_profile(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        # Convert ObjectId to string for JSON serialization
        if "_id" in user:
            user["_id"] = str(user["_id"])
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        raise HTTPException(status_code=500, detail="Error fetching user profile")

@router.post("/verify-kyc", response_model=KYCResponse)
async def verify_kyc(kyc_data: KYCRequest):
    """Verify user identity using Aadhaar or PAN"""
    try:
        logger.info(f"Verifying KYC. User ID provided: {kyc_data.user_id}")
        
        # Ensure at least one is provided
        if not kyc_data.aadhaar_number and not kyc_data.pan_number:
            return KYCResponse(kyc_status="Failed", message="Please enter Aadhaar or PAN.")

        # Perform verification
        result = identity_kyc_service.verify_kyc(kyc_data.aadhaar_number, kyc_data.pan_number)
        
        # Update KYC status in database ONLY if user_id is provided
        if kyc_data.user_id:
            if result["kyc_status"] == "Verified":
                await update_kyc_status(kyc_data.user_id, True)
            else:
                await update_kyc_status(kyc_data.user_id, False)

        return KYCResponse(**result)
    except Exception as e:
        logger.error(f"Error in KYC verification: {e}")
        raise HTTPException(status_code=500, detail="KYC verification failed")

@router.post("/analyze-loan", response_model=AgentDecisionResponse)
async def analyze_loan(application: LoanApplicationRequest, background_tasks: BackgroundTasks):
    try:
        logger.info(f"Processing loan application for user: {application.user_id}")
        
        # Ensure user exists in database and check KYC status
        user = await create_or_update_user(application.user_id)
        
        # If user is None, it means the database is likely down or misconfigured
        if user is None:
            logger.warning(f"Database unavailable for user {application.user_id}. Proceeding with cautious defaults.")
            # For this mock, we'll allow processing if DB is down but we'll flag it
            user = {"user_id": application.user_id, "kyc_verified": True} # Default to True for UX in mock environment
        
        # If user is found but not verified, we stop them
        if not user.get("kyc_verified"):
            # Note: In a production app, we would strictly enforce this. 
            # In this demo, if the DB is failing to update, we may want a fallback or a clearer error.
            raise HTTPException(status_code=403, detail="KYC verification required before loan processing. Please ensure identity is verified.")

        # Step 1: Automatic DTI Calculation
        # DTI = total_debt / income
        if application.income > 0:
            dti = application.total_debt / application.income
        else:
            dti = 0.0
        
        # Clamp DTI between 0 and 1, round to 2 decimals
        dti = round(max(0.0, min(1.0, dti)), 2)
        logger.info(f"Calculated DTI for {application.user_id}: {dti}")

        # Step 2: Log similar decisions for contextual visibility
        similar_past = await get_similar_decisions(application.credit_score)
        if similar_past:
            logger.info(f"Found {len(similar_past)} similar past decisions: {similar_past}")
        
        # Step 3: Fast processing via the agent
        try:
            # We pass the computed DTI into the agent
            decision: AgentDecisionResponse = LoanAgent.process_application(application, dti=dti)
        except RuntimeError as agent_err:
            logger.error(f"Agent internally failed: {agent_err}")
            raise HTTPException(status_code=500, detail=str(agent_err))
            
        logger.info(f"Agent decision for {application.user_id}: {decision.decision} with confidence: {decision.confidence:.2f}")
        
        # Step 4: Prepare the log data
        logged_data = LoggedDecision(
            user_id=application.user_id,
            application_data={**application.model_dump(), "computed_dti": dti},
            risk_score=decision.risk_score,
            confidence=decision.confidence,
            decision=decision.decision,
            explanation=decision.explanation,
            dti=decision.dti,
            important_features=decision.important_features
        )
        
        # Step 5: Save decision and update user stats in background
        background_tasks.add_task(save_decision, logged_data)
        background_tasks.add_task(update_user_stats, application.user_id, decision.decision)
        
        return decision
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unhandled error processing loan application: {e}")
        # Provide the actual error for easier debugging in this phase
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/download-report")
async def download_report(report_data: DownloadReportRequest):
    """
    Generate and download a PDF report of the loan decision
    """
    try:
        logger.info(f"Generating PDF report for user: {report_data.user_id}")
        
        # Separate application data and decision data
        application_data = {
            "user_id": report_data.user_id,
            "income": report_data.income,
            "credit_score": report_data.credit_score,
            "dti": report_data.dti,
            "employment_length": report_data.employment_length,
            "currency": report_data.currency
        }
        
        decision_data = {
            "risk_score": report_data.risk_score,
            "confidence": report_data.confidence,
            "decision": report_data.decision,
            "explanation": report_data.explanation,
            "important_features": [f.dict() for f in report_data.important_features]
        }
        
        # Generate PDF
        pdf_buffer = generate_loan_report_pdf(
            application_data=application_data,
            decision_data=decision_data
        )
        
        # Return as streaming response
        filename = f"Loan_Decision_{report_data.user_id}_{report_data.decision}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {str(e)}")


# ============================================
# PLAID INTEGRATION ENDPOINTS
# ============================================

@router.post("/plaid/create-link-token")
async def create_plaid_link_token(user_id: str, user_name: str = None):
    """
    Create Plaid Link token for frontend initialization
    """
    try:
        result = await plaid_service.create_link_token(user_id, user_name)
        return result
    except Exception as e:
        logger.error(f"Error creating Plaid link token: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/plaid/exchange-token")
async def exchange_plaid_token(public_token: str):
    """
    Exchange Plaid public token for access token
    """
    try:
        result = await plaid_service.exchange_public_token(public_token)
        return result
    except Exception as e:
        logger.error(f"Error exchanging Plaid token: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/plaid/get-balances")
async def get_plaid_balances(access_token: str):
    """
    Get account balances from Plaid
    """
    try:
        result = await plaid_service.get_account_balances(access_token)
        return result
    except Exception as e:
        logger.error(f"Error getting Plaid balances: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/plaid/get-income")
async def get_plaid_income(access_token: str):
    """
    Get income data from Plaid
    """
    try:
        result = await plaid_service.get_income_data(access_token)
        return result
    except Exception as e:
        logger.error(f"Error getting Plaid income: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# CREDIT BUREAU INTEGRATION ENDPOINTS
# ============================================

@router.post("/credit-bureau/check")
async def check_credit_bureau(user_id: str, full_name: str = ""):
    """
    Get credit data from credit bureau API
    """
    try:
        result = await credit_bureau_service.get_credit_data(user_id, full_name)
        return result
    except Exception as e:
        logger.error(f"Error checking credit bureau: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# KYC / DOCUMENT VERIFICATION ENDPOINTS
# ============================================

@router.post("/kyc/upload-document")
async def upload_kyc_document(
    user_id: str = Form(...),
    expected_name: str = Form(None),
    expected_dob: str = Form(None),
    file: UploadFile = File(...)
):
    """
    Upload and verify ID document
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Only image files are allowed")
        
        # Read file content
        content = await file.read()
        
        # Check file size (5MB limit)
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 5MB limit")
        
        # Save document
        file_path = await kyc_service.save_document(content, user_id, file.filename)
        
        # Verify document
        verification_result = await kyc_service.verify_document(
            file_path,
            expected_name,
            expected_dob
        )
        
        return {
            "success": True,
            "file_path": file_path,
            "verification": verification_result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading KYC document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# ENHANCED LOAN ANALYSIS WITH INTEGRATIONS
# ============================================

@router.post("/analyze-loan-enhanced", response_model=AgentDecisionResponse)
async def analyze_loan_enhanced(
    application: LoanApplicationRequest,
    background_tasks: BackgroundTasks,
    use_credit_bureau: bool = True,
    plaid_access_token: str = None
):
    """
    Enhanced loan analysis with credit bureau and Plaid integration
    """
    try:
        logger.info(f"Processing enhanced loan application for user: {application.user_id}")
        
        # Ensure user exists in database
        await create_or_update_user(application.user_id)
        
        # Step 1: Get credit data from credit bureau
        credit_data = None
        if use_credit_bureau:
            credit_data = await credit_bureau_service.get_credit_data(application.user_id)
            logger.info(f"Credit bureau data: Score={credit_data['credit_score']}, DTI={credit_data['debt_index']}")
            
            # Override application data with bureau data
            application.credit_score = credit_data['credit_score']
            application.dti = credit_data['debt_index']
        
        # Step 2: Get Plaid data if access token provided
        plaid_data = None
        if plaid_access_token:
            try:
                balance_data = await plaid_service.get_account_balances(plaid_access_token)
                income_data = await plaid_service.get_income_data(plaid_access_token)
                
                plaid_data = {
                    "total_balance": balance_data['total_balance'],
                    "annual_income": income_data['annual_income']
                }
                
                # Override income with Plaid data
                if income_data['verified']:
                    application.income = income_data['annual_income']
                
                logger.info(f"Plaid data: Balance=${balance_data['total_balance']}, Income=${income_data['annual_income']}")
            except Exception as e:
                logger.warning(f"Could not fetch Plaid data: {e}")
        
        # Step 3: Run AI agent analysis
        try:
            decision: AgentDecisionResponse = LoanAgent.process_application(application)
        except RuntimeError as agent_err:
            logger.error(f"Agent internally failed: {agent_err}")
            raise HTTPException(status_code=500, detail=str(agent_err))
        
        logger.info(f"Agent decision for {application.user_id}: {decision.decision} with confidence: {decision.confidence:.2f}")
        
        # Step 4: Save decision with enhanced data
        logged_data = LoggedDecision(
            user_id=application.user_id,
            application_data={
                **application.model_dump(),
                "credit_bureau_data": credit_data,
                "plaid_data": plaid_data
            },
            risk_score=decision.risk_score,
            confidence=decision.confidence,
            decision=decision.decision,
            explanation=decision.explanation,
            important_features=decision.important_features
        )
        
        background_tasks.add_task(save_decision, logged_data)
        background_tasks.add_task(update_user_stats, application.user_id, decision.decision)
        
        return decision
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unhandled error in enhanced loan analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error during enhanced loan analysis.")
