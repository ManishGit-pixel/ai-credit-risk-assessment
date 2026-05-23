"""
Credit Bureau Integration Service
Calls the mock credit bureau API to get credit data
"""

import httpx
from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class CreditBureauService:
    def __init__(self):
        self.api_url = settings.CREDIT_BUREAU_API_URL
        self.api_key = settings.CREDIT_BUREAU_API_KEY
    
    async def get_credit_data(self, user_id: str, full_name: str = "") -> dict:
        """
        Call credit bureau API to get credit score and debt information
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/api/v1/credit-check",
                    json={
                        "user_id": user_id,
                        "ssn_last_4": "0000",
                        "full_name": full_name
                    },
                    headers={
                        "X-API-Key": self.api_key,
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Successfully fetched credit data for user: {user_id}")
                    return {
                        "success": True,
                        "credit_score": data.get("credit_velocity", 650),
                        "debt_index": data.get("debt_index", 0.35),
                        "credit_history_months": data.get("credit_history_months", 60),
                        "total_accounts": data.get("total_accounts", 5),
                        "delinquent_accounts": data.get("delinquent_accounts", 0),
                        "credit_utilization": data.get("credit_utilization", 0.3),
                        "payment_history_score": data.get("payment_history_score", 75),
                        "bureau_name": data.get("bureau_name", "MockExperian")
                    }
                else:
                    logger.error(f"Credit bureau API returned status {response.status_code}")
                    return self._get_fallback_data(user_id)
        
        except httpx.ConnectError:
            logger.warning(f"Credit bureau API not available, using fallback data")
            return self._get_fallback_data(user_id)
        
        except Exception as e:
            logger.error(f"Error calling credit bureau API: {e}")
            return self._get_fallback_data(user_id)
    
    def _get_fallback_data(self, user_id: str) -> dict:
        """
        Return fallback credit data if API is unavailable
        """
        return {
            "success": False,
            "credit_score": 650,  # Default middle score
            "debt_index": 0.35,
            "credit_history_months": 60,
            "total_accounts": 5,
            "delinquent_accounts": 0,
            "credit_utilization": 0.3,
            "payment_history_score": 70,
            "bureau_name": "Fallback"
        }

# Singleton instance
credit_bureau_service = CreditBureauService()
