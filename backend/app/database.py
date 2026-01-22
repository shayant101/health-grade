from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
from .config import settings
import logging

class DatabaseConnection:
    """
    Manages asynchronous MongoDB connection using Motor driver.
    Provides methods for database connection and management.
    """
    _instance = None
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

    def __new__(cls):
        """
        Singleton pattern implementation to ensure only one database connection.
        """
        if not cls._instance:
            cls._instance = super(DatabaseConnection, self).__new__(cls)
        return cls._instance

    async def connect(self) -> AsyncIOMotorDatabase:
        """
        Establish an asynchronous connection to MongoDB.
        
        Returns:
            AsyncIOMotorDatabase: Connected database instance
        
        Raises:
            ConnectionFailure: If unable to connect to MongoDB
        """
        try:
            # Create async motor client
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            
            # Extract database name from connection string (default to 'restaurantgrader')
            db_name = self.client.get_database_name() or 'restaurantgrader'
            
            # Create database instance
            self.db = self.client[db_name]
            
            # Verify connection
            await self.db.command('ping')
            
            logging.info(f"Successfully connected to MongoDB database: {db_name}")
            return self.db
        
        except ConnectionFailure as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def close(self):
        """
        Close the MongoDB connection safely.
        """
        if self.client:
            self.client.close()
            logging.info("MongoDB connection closed")

# Create a singleton database connection instance
database = DatabaseConnection()