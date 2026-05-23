# 🏦 AI-Powered Credit Risk Assessment System

A complete loan underwriting system with AI risk prediction, credit bureau integration, and explainable AI using SHAP.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- npm or yarn

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd ai-agent-for-credit-risk-assessment
```

2. **Install backend dependencies**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. **Train the ML model**
```bash
python models/train_dummy.py
```

4. **Install frontend dependencies**
```bash
cd frontend
npm install
cd ..
```

5. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

## 🎯 Running the Application

### Option 1: Run in Separate Terminals (Recommended)

**Terminal 1 - Backend:**
```bash
./start_backend.sh
```
Backend will run on: http://localhost:8000

**Terminal 2 - Frontend:**
```bash
./start_frontend.sh
```
Frontend will run on: http://localhost:5173

**Terminal 3 - Credit Bureau API (Optional):**
```bash
./start_credit_bureau.sh
```
Credit Bureau API will run on: http://localhost:8001

### Option 2: Manual Start

**Backend:**
```bash
source .venv/bin/activate
python main.py
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## 📊 Project Structure

```
.
├── agent/                      # AI Agent logic
│   ├── core.py                # Main agent implementation
│   └── memory.py              # Decision memory/history
│
├── api/                       # API layer
│   ├── routes.py              # All API endpoints
│   └── schemas.py             # Pydantic models
│
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API service layer
│   │   └── contexts/         # React contexts
│   └── package.json
│
├── models/                    # ML models
│   ├── train_dummy.py        # Model training script
│   ├── dummy_model.pkl       # Trained model (generated)
│   └── schemas.py            # Model schemas
│
├── services/                  # External services
│   ├── credit_bureau_service.py  # Credit bureau integration
│   ├── plaid_service.py          # Plaid integration
│   └── kyc_service.py            # KYC verification
│
├── tools/                     # Core ML tools
│   ├── risk_model.py         # Risk prediction
│   ├── explainability.py     # SHAP explanations
│   ├── decision.py           # Decision engine
│   └── user_data.py          # User data fetching
│
├── utils/                     # Utilities
│   ├── db.py                 # Database operations
│   ├── logger.py             # Logging configuration
│   └── report_generator.py  # PDF report generation
│
├── uploads/                   # File uploads directory
│
├── main.py                    # FastAPI application
├── config.py                  # Configuration
├── database.py                # MongoDB setup
├── requirements.txt           # Python dependencies
├── start_backend.sh          # Backend startup script
├── start_frontend.sh         # Frontend startup script
└── start_credit_bureau.sh    # Credit Bureau API startup script
```

## 🔌 API Endpoints

### Loan Analysis
- `POST /analyze-loan-complete` - Complete loan analysis with all integrations
- `POST /analyze-loan` - Standard loan analysis
- `POST /analyze-loan-enhanced` - Enhanced with Plaid integration

### Credit Bureau
- `POST /credit-bureau/check` - Check credit data

### Plaid Integration
- `POST /plaid/create-link-token` - Create Plaid Link token
- `POST /plaid/exchange-token` - Exchange public token
- `POST /plaid/get-balances` - Get account balances
- `POST /plaid/get-income` - Get income data

### KYC
- `POST /kyc/upload-document` - Upload ID document

### User Management
- `GET /user/{user_id}` - Get user profile

### Reports
- `POST /download-report` - Generate PDF report

### System
- `GET /health` - Health check

## 📝 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Testing

### Test the Complete Endpoint
```bash
curl -X POST "http://localhost:8000/analyze-loan-complete" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "income": 75000,
    "credit_score": 720,
    "dti": 0.35,
    "employment_length": 5,
    "currency": "USD"
  }'
```

### Run Test Suite
```bash
python test_analyze_loan_endpoint.py
```

## 🔧 Configuration

Edit `.env` file:

```env
# LLM Configuration
USE_LOCAL_LLM=True
OPENAI_API_KEY=your_key_here

# Database
MONGO_URI=mongodb://localhost:27017
MONGODB_DB_NAME=loan_agent_db

# Risk Thresholds
THRESHOLD_APPROVE=0.4
THRESHOLD_REJECT=0.7

# Plaid (Optional)
PLAID_CLIENT_ID=your_client_id
PLAID_SECRET=your_secret
PLAID_ENV=sandbox

# Credit Bureau API
CREDIT_BUREAU_API_URL=http://localhost:8001
CREDIT_BUREAU_API_KEY=mock_api_key_12345
```

## 🎯 Features

### Core Features
- ✅ AI-powered risk prediction using XGBoost
- ✅ SHAP explainability for transparent decisions
- ✅ Credit bureau API integration
- ✅ Decision engine with configurable thresholds
- ✅ MongoDB for data persistence
- ✅ Background task processing
- ✅ Comprehensive logging

### Integrations
- ✅ Plaid for bank account verification
- ✅ KYC document verification
- ✅ PDF report generation
- ✅ User profile management

### Frontend
- ✅ React with Vite
- ✅ Modern UI with Tailwind CSS
- ✅ Real-time loan analysis
- ✅ SHAP visualization
- ✅ User dashboard

## 🔍 How It Works

### Loan Analysis Flow

1. **User Input** - Applicant submits loan application
2. **Credit Bureau** - System fetches real credit data from API
3. **AI Prediction** - XGBoost model predicts default probability
4. **SHAP Analysis** - Generates feature importance explanations
5. **Decision Engine** - Applies business rules for final decision
6. **Database** - Saves complete audit trail
7. **Response** - Returns decision with explanations

### Decision Logic

```
Risk Score < 0.4  → Approve
Risk Score ≥ 0.7  → Reject
0.4 ≤ Risk < 0.7  → Manual Review
```

## 📊 Response Format

```json
{
  "risk_score": 0.0595,
  "confidence": 0.9495,
  "decision": "Approve",
  "explanation": "The applicant is classified as low risk...",
  "important_features": [
    {
      "feature": "credit_score",
      "impact": "High positive impact reducing risk"
    },
    {
      "feature": "dti",
      "impact": "Moderate positive impact reducing risk"
    }
  ]
}
```

## 🛠️ Development

### Backend Development
```bash
source .venv/bin/activate
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Code Formatting
```bash
# Python
black .
isort .

# JavaScript
cd frontend
npm run lint
```

## 📦 Dependencies

### Backend
- FastAPI - Modern web framework for building REST APIs with automatic OpenAPI documentation and request validation.
- Motor - Asynchronous MongoDB driver enabling non-blocking database operations for improved server performance.
- XGBoost - Gradient boosting library used for training the credit risk prediction and default probability model.
- SHAP - Framework for generating explainable AI insights by computing feature importance and decision explanations.
- Pydantic - Data validation and serialization library for enforcing type safety on API request/response schemas.
- httpx - Asynchronous HTTP client for making requests to external services (Plaid, Credit Bureau API, KYC).

### Frontend
- React JS (ES6+) : Library for building component-based user interface for applicants and loan officers with state management and component lifecycle handling.
- Vite : Fast build tool with development server and hot module replacement for accelerated UI development.
- Axios : HTTP client for asynchronous communication between frontend and backend API server with built-in interceptors for request/response handling.
- React Router : Manages client-side routing across multiple pages (Home, Dashboard, Loan Application, KYC Upload) without full page reloads.
- Tailwind CSS : Utility-first CSS framework for creating responsive financial dashboard and application forms with consistent styling.

## 🚨 Troubleshooting

### Backend won't start
- Check if port 8000 is available: `lsof -i :8000`
- Verify virtual environment is activated
- Check if all dependencies are installed: `pip list`

### Frontend won't start
- Check if port 5173 is available
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Clear npm cache: `npm cache clean --force`

### Model not found
- Train the model: `python models/train_dummy.py`
- Check if `models/dummy_model.pkl` exists

### MongoDB connection error
- Install MongoDB: `brew install mongodb-community`
- Start MongoDB: `brew services start mongodb-community`
- Or the system will use fallback mode without persistence

## 📄 License

MIT License

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation in `/docs`
- Review API docs at http://localhost:8000/docs

## 🎉 Acknowledgments

- XGBoost for the ML framework
- SHAP for explainability
- FastAPI for the excellent web framework
- React team for the frontend framework
# miniproject2B
# AI-Banking
