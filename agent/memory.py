from utils.db import get_db
from api.schemas import LoggedDecision
from utils.logger import get_logger

logger = get_logger(__name__)

async def save_decision(decision_data: LoggedDecision):
    """
    Save the agent's final decision and application data to MongoDB.
    """
    db = get_db()
    if db is not None:
        try:
            collection = db["decisions"]
            # Convert to dict and insert
            result = await collection.insert_one(decision_data.model_dump())
            logger.info(f"Saved decision to MongoDB with id: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to save decision to MongoDB: {e}")
            return None
    else:
        logger.warning("MongoDB not connected. Skipping save.")
        return None

async def get_similar_decisions(credit_score: int, limit: int = 3) -> list:
    """
    Fetch recent decisions from MongoDB that have a similar credit score (+/- 20 pts).
    """
    db = get_db()
    if db is not None:
        try:
            collection = db["decisions"]
            cursor = collection.find({
                "application_data.credit_score": {
                    "$gte": credit_score - 20,
                    "$lte": credit_score + 20
                }
            }).sort("timestamp", -1).limit(limit)
            
            results = await cursor.to_list(length=limit)
            
            # Simple list of dicts returning stripped down logging data
            return [{"decision": r.get("decision"), "risk_score": r.get("risk_score")} for r in results]
        except Exception as e:
            logger.error(f"Failed to fetch similar decisions: {e}")
            return []
    logger.warning("MongoDB not connected. Skipping fetch.")
    return []
