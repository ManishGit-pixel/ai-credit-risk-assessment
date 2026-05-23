from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from utils.logger import get_logger
from datetime import datetime

logger = get_logger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db_instance = MongoDB()

async def connect_to_db():
    try:
        logger.info(f"Connecting to MongoDB at {settings.MONGO_URI}...")
        db_instance.client = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
        db_instance.db = db_instance.client[settings.MONGODB_DB_NAME]
        # Forced ping to verify connection
        await db_instance.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB.")
    except Exception as e:
        logger.warning(f"Could not connect to MongoDB: {e}. System will run with in-memory fallbacks.")
        db_instance.client = None
        db_instance.db = None

async def close_db_connection():
    if db_instance.client:
        logger.info("Closing MongoDB connection.")
        db_instance.client.close()

def get_db():
    return db_instance.db

# User Profile Management
async def get_user_profile(user_id: str):
    """Retrieve user profile from MongoDB"""
    try:
        db = get_db()
        if db is None:
            return None
        user = await db.users.find_one({"user_id": user_id})
        return user
    except Exception as e:
        logger.error(f"Error fetching user profile: {e}")
        return None

async def create_or_update_user(user_id: str, name: str = None, email: str = None, phone: str = None):
    """Create or update user profile"""
    try:
        db = get_db()
        if db is None:
            return None
        
        existing_user = await db.users.find_one({"user_id": user_id})
        
        if existing_user:
            # Update existing user
            update_data = {}
            if name:
                update_data["name"] = name
            if email:
                update_data["email"] = email
            if phone:
                update_data["phone"] = phone
            
            if update_data:
                await db.users.update_one(
                    {"user_id": user_id},
                    {"$set": update_data}
                )
            return await db.users.find_one({"user_id": user_id})
        else:
            # Create new user
            user_data = {
                "user_id": user_id,
                "name": name or user_id,
                "email": email or f"{user_id}@example.com",
                "phone": phone,
                "created_at": datetime.utcnow(),
                "total_applications": 0,
                "approved_count": 0,
                "rejected_count": 0,
                "review_count": 0,
                "kyc_verified": False
            }
            await db.users.insert_one(user_data)
            return user_data
    except Exception as e:
        logger.error(f"Error creating/updating user: {e}")
        return None

async def update_user_stats(user_id: str, decision: str):
    """Update user application statistics"""
    try:
        db = get_db()
        if db is None:
            return
        
        update_fields = {"$inc": {"total_applications": 1}}
        
        if decision.lower() == "approve":
            update_fields["$inc"]["approved_count"] = 1
        elif decision.lower() == "reject":
            update_fields["$inc"]["rejected_count"] = 1
        else:
            update_fields["$inc"]["review_count"] = 1
        
        await db.users.update_one(
            {"user_id": user_id},
            update_fields,
            upsert=True
        )
        logger.info(f"Updated stats for user {user_id}: {decision}")
    except Exception as e:
        logger.error(f"Error updating user stats: {e}")

async def update_kyc_status(user_id: str, status: bool):
    """Update user KYC verification status"""
    try:
        db = get_db()
        if db is None:
            return
        
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"kyc_verified": status}},
            upsert=True
        )
        logger.info(f"Updated KYC status for user {user_id}: {status}")
    except Exception as e:
        logger.error(f"Error updating KYC status: {e}")
