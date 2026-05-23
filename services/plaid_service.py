"""
Plaid API Integration Service
Handles Plaid Link token creation and data exchange
"""

from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.income_verification_paystubs_get_request import IncomeVerificationPaystubsGetRequest
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from config import settings
from utils.logger import get_logger
import os

logger = get_logger(__name__)

class PlaidService:
    def __init__(self):
        # Configure Plaid client
        configuration = Configuration(
            host=self._get_plaid_host(),
            api_key={
                'clientId': settings.PLAID_CLIENT_ID,
                'secret': settings.PLAID_SECRET,
            }
        )
        
        api_client = ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)
    
    def _get_plaid_host(self):
        """Get Plaid API host based on environment"""
        env_map = {
            'sandbox': 'https://sandbox.plaid.com',
            'development': 'https://development.plaid.com',
            'production': 'https://production.plaid.com'
        }
        return env_map.get(settings.PLAID_ENV, 'https://sandbox.plaid.com')
    
    async def create_link_token(self, user_id: str, user_name: str = None):
        """
        Create a Plaid Link token for frontend initialization
        """
        try:
            request = LinkTokenCreateRequest(
                user=LinkTokenCreateRequestUser(
                    client_user_id=user_id
                ),
                client_name="AI Loan Underwriting",
                products=[Products("auth"), Products("transactions"), Products("income")],
                country_codes=[CountryCode('US')],
                language='en',
                redirect_uri=settings.FRONTEND_ORIGIN if settings.PLAID_ENV != 'sandbox' else None
            )
            
            response = self.client.link_token_create(request)
            logger.info(f"Created Plaid link token for user: {user_id}")
            
            return {
                "link_token": response['link_token'],
                "expiration": response['expiration']
            }
        
        except Exception as e:
            logger.error(f"Error creating Plaid link token: {e}")
            raise Exception(f"Failed to create Plaid link token: {str(e)}")
    
    async def exchange_public_token(self, public_token: str):
        """
        Exchange public token for access token
        """
        try:
            request = ItemPublicTokenExchangeRequest(
                public_token=public_token
            )
            
            response = self.client.item_public_token_exchange(request)
            
            return {
                "access_token": response['access_token'],
                "item_id": response['item_id']
            }
        
        except Exception as e:
            logger.error(f"Error exchanging public token: {e}")
            raise Exception(f"Failed to exchange public token: {str(e)}")
    
    async def get_account_balances(self, access_token: str):
        """
        Get account balances from Plaid
        """
        try:
            request = AccountsBalanceGetRequest(
                access_token=access_token
            )
            
            response = self.client.accounts_balance_get(request)
            
            accounts = []
            total_balance = 0
            
            for account in response['accounts']:
                account_data = {
                    "account_id": account['account_id'],
                    "name": account['name'],
                    "type": account['type'],
                    "subtype": account['subtype'],
                    "balance": account['balances']['current'],
                    "available": account['balances'].get('available'),
                    "currency": account['balances']['iso_currency_code']
                }
                accounts.append(account_data)
                
                if account['balances']['current']:
                    total_balance += account['balances']['current']
            
            return {
                "accounts": accounts,
                "total_balance": total_balance
            }
        
        except Exception as e:
            logger.error(f"Error getting account balances: {e}")
            raise Exception(f"Failed to get account balances: {str(e)}")
    
    async def get_income_data(self, access_token: str):
        """
        Get income verification data from Plaid
        """
        try:
            # In sandbox, we'll simulate income data
            # In production, use actual Plaid income verification
            
            # For sandbox, return mock data
            return {
                "annual_income": 85000,  # This would come from Plaid in production
                "income_sources": [
                    {
                        "employer": "Tech Company Inc",
                        "income": 85000,
                        "frequency": "annual"
                    }
                ],
                "verified": True
            }
        
        except Exception as e:
            logger.error(f"Error getting income data: {e}")
            return {
                "annual_income": 0,
                "income_sources": [],
                "verified": False
            }

# Singleton instance
plaid_service = PlaidService()
