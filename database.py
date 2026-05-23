"""
MongoDB Database Connection and Operations
Production-ready async MongoDB setup using Motor
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
from contextlib import asynccontextmanager
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    """
    MongoDB Database Manager
    Handles connection lifecycle and provides helper methods
    """
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self._connection_string: Optional[str] = None
        self._database_name: Optional[str] = None
    
    async def connect(
        self,
        connection_string: Optional[str] = None,
        database_name: Optional[str] = None,
        max_pool_size: int = 10,
        min_pool_size: int = 1,
        server_selection_timeout_ms: int = 5000
    ) -> None:
        """
        Connect to MongoDB database
        
        Args:
            connection_string: MongoDB connection URI
            database_name: Name of the database to use
            max_pool_size: Maximum number of connections in the pool
            min_pool_size: Minimum number of connections in the pool
            server_selection_timeout_ms: Timeout for server selection
        
        Raises:
            ConnectionFailure: If connection to MongoDB fails
        """
        try:
            # Get connection details from environment or parameters
            self._connection_string = connection_string or os.getenv(
                "MONGODB_URI",
                "mongodb://localhost:27017"
            )
            self._database_name = database_name or os.getenv(
                "MONGODB_DB_NAME",
                "loan_agent_db"
            )
            
            logger.info(f"Connecting to MongoDB at {self._connection_string}")
            
            # Create MongoDB client with connection pooling
            self.client = AsyncIOMotorClient(
                self._connection_string,
                maxPoolSize=max_pool_size,
                minPoolSize=min_pool_size,
                serverSelectionTimeoutMS=server_selection_timeout_ms,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
            )
            
            # Get database instance
            self.db = self.client[self._database_name]
            
            # Verify connection by pinging the server
            await self.client.admin.command('ping')
            
            logger.info(f"Successfully connected to MongoDB database: {self._database_name}")
            
            # Create indexes for better performance
            await self._create_indexes()
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise ConnectionFailure(f"Could not connect to MongoDB: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during MongoDB connection: {e}")
            raise
    
    async def disconnect(self) -> None:
        """
        Close MongoDB connection
        """
        if self.client:
            logger.info("Closing MongoDB connection")
            self.client.close()
            self.client = None
            self.db = None
            logger.info("MongoDB connection closed")
    
    async def _create_indexes(self) -> None:
        """
        Create database indexes for better query performance
        """
        try:
            # Index on applicant_id for fast lookups
            await self.db.loans.create_index("applicant_id")
            
            # Index on status for filtering
            await self.db.loans.create_index("status")
            
            # Index on created_at for sorting
            await self.db.loans.create_index("created_at")
            
            # Compound index for common queries
            await self.db.loans.create_index([
                ("applicant_id", 1),
                ("created_at", -1)
            ])
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Could not create indexes: {e}")
    
    def get_collection(self, collection_name: str) -> AsyncIOMotorCollection:
        """
        Get a collection from the database
        
        Args:
            collection_name: Name of the collection
        
        Returns:
            AsyncIOMotorCollection instance
        
        Raises:
            RuntimeError: If database is not connected
        """
        if not self.db:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.db[collection_name]
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check database health
        
        Returns:
            Dictionary with health status
        """
        try:
            if not self.client:
                return {
                    "status": "disconnected",
                    "message": "Database client not initialized"
                }
            
            # Ping the database
            await self.client.admin.command('ping')
            
            # Get server info
            server_info = await self.client.server_info()
            
            return {
                "status": "connected",
                "database": self._database_name,
                "mongodb_version": server_info.get("version", "unknown"),
                "message": "Database is healthy"
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "error",
                "message": str(e)
            }


# Global database instance
database = Database()


# ============================================
# LOAN APPLICATION OPERATIONS
# ============================================

async def insert_loan_application(application_data: Dict[str, Any]) -> str:
    """
    Insert a new loan application into the database
    
    Args:
        application_data: Dictionary containing loan application data
    
    Returns:
        String ID of the inserted document
    
    Raises:
        RuntimeError: If database is not connected
        Exception: If insertion fails
    """
    try:
        # Get loans collection
        loans_collection = database.get_collection("loans")
        
        # Add timestamps
        now = datetime.utcnow()
        application_data["created_at"] = now
        application_data["updated_at"] = now
        
        # Set default status if not provided
        if "status" not in application_data:
            application_data["status"] = "pending"
        
        # Insert document
        result = await loans_collection.insert_one(application_data)
        
        logger.info(f"Inserted loan application with ID: {result.inserted_id}")
        
        return str(result.inserted_id)
    
    except Exception as e:
        logger.error(f"Failed to insert loan application: {e}")
        raise Exception(f"Database insertion failed: {e}")


async def get_loan_application(application_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a loan application by ID
    
    Args:
        application_id: MongoDB document ID or applicant_id
    
    Returns:
        Dictionary containing loan application data or None if not found
    """
    try:
        from bson import ObjectId
        
        loans_collection = database.get_collection("loans")
        
        # Try to find by MongoDB _id first
        try:
            result = await loans_collection.find_one({"_id": ObjectId(application_id)})
            if result:
                result["id"] = str(result.pop("_id"))
                return result
        except:
            pass
        
        # Try to find by applicant_id
        result = await loans_collection.find_one({"applicant_id": application_id})
        if result:
            result["id"] = str(result.pop("_id"))
            return result
        
        return None
    
    except Exception as e:
        logger.error(f"Failed to retrieve loan application: {e}")
        raise


async def update_loan_application(
    application_id: str,
    update_data: Dict[str, Any]
) -> bool:
    """
    Update an existing loan application
    
    Args:
        application_id: MongoDB document ID
        update_data: Dictionary containing fields to update
    
    Returns:
        True if update was successful, False otherwise
    """
    try:
        from bson import ObjectId
        
        loans_collection = database.get_collection("loans")
        
        # Add updated timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        # Update document
        result = await loans_collection.update_one(
            {"_id": ObjectId(application_id)},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            logger.info(f"Updated loan application: {application_id}")
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"Failed to update loan application: {e}")
        raise


async def get_loan_applications(
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    applicant_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve multiple loan applications with filtering and pagination
    
    Args:
        skip: Number of documents to skip
        limit: Maximum number of documents to return
        status: Filter by status (optional)
        applicant_id: Filter by applicant_id (optional)
    
    Returns:
        List of loan application dictionaries
    """
    try:
        loans_collection = database.get_collection("loans")
        
        # Build query filter
        query = {}
        if status:
            query["status"] = status
        if applicant_id:
            query["applicant_id"] = applicant_id
        
        # Execute query with pagination
        cursor = loans_collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        
        # Convert cursor to list
        applications = []
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            applications.append(doc)
        
        return applications
    
    except Exception as e:
        logger.error(f"Failed to retrieve loan applications: {e}")
        raise


async def count_loan_applications(
    status: Optional[str] = None,
    applicant_id: Optional[str] = None
) -> int:
    """
    Count loan applications with optional filtering
    
    Args:
        status: Filter by status (optional)
        applicant_id: Filter by applicant_id (optional)
    
    Returns:
        Number of matching documents
    """
    try:
        loans_collection = database.get_collection("loans")
        
        # Build query filter
        query = {}
        if status:
            query["status"] = status
        if applicant_id:
            query["applicant_id"] = applicant_id
        
        # Count documents
        count = await loans_collection.count_documents(query)
        
        return count
    
    except Exception as e:
        logger.error(f"Failed to count loan applications: {e}")
        raise


async def delete_loan_application(application_id: str) -> bool:
    """
    Delete a loan application
    
    Args:
        application_id: MongoDB document ID
    
    Returns:
        True if deletion was successful, False otherwise
    """
    try:
        from bson import ObjectId
        
        loans_collection = database.get_collection("loans")
        
        # Delete document
        result = await loans_collection.delete_one({"_id": ObjectId(application_id)})
        
        if result.deleted_count > 0:
            logger.info(f"Deleted loan application: {application_id}")
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"Failed to delete loan application: {e}")
        raise


# ============================================
# CONTEXT MANAGER FOR DATABASE LIFECYCLE
# ============================================

@asynccontextmanager
async def get_database():
    """
    Context manager for database operations
    Ensures proper connection and cleanup
    """
    if not database.db:
        await database.connect()
    try:
        yield database
    finally:
        # Connection is kept alive for the application lifetime
        # Only close on application shutdown
        pass


# ============================================
# STARTUP AND SHUTDOWN FUNCTIONS
# ============================================

async def connect_to_database():
    """
    Connect to database on application startup
    """
    await database.connect()


async def close_database_connection():
    """
    Close database connection on application shutdown
    """
    await database.disconnect()
