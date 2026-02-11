from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
from .config import settings
import logging
from datetime import datetime
from typing import Optional
from bson import ObjectId

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
            cls._instance = super().__new__(cls)
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
            
            # Create database instance
            self.db = self.client['restaurantgrader']
            
            # Verify connection
            await self.db.command('ping')
            
            logging.info(f"Successfully connected to MongoDB database: restaurantgrader")
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

# Scan CRUD Methods
async def create_scan(scan_data: dict) -> dict:
    """
    Insert a new scan into the database.
    
    Args:
        scan_data (dict): Scan data to be inserted
    
    Returns:
        dict: Inserted scan with _id
    """
    try:
        # Ensure created_at is set if not provided
        if 'created_at' not in scan_data:
            scan_data['created_at'] = datetime.utcnow()
        
        # Insert scan into database
        result = await database.db['scans'].insert_one(scan_data)
        
        # Retrieve and return the inserted scan
        scan = await database.db['scans'].find_one({'_id': result.inserted_id})
        
        # Convert ObjectId to string
        scan['_id'] = str(scan['_id'])
        
        return scan
    except Exception as e:
        logging.error(f"Error creating scan: {e}")
        raise

async def get_scan_by_id(scan_id: str) -> dict | None:
    """
    Retrieve a scan by its ID.
    
    Args:
        scan_id (str): Unique scan identifier
    
    Returns:
        dict | None: Scan details or None if not found
    """
    try:
        # Find scan by ID
        scan = await database.db['scans'].find_one({'_id': ObjectId(scan_id)})
        
        if scan:
            # Convert ObjectId to string
            scan['_id'] = str(scan['_id'])
        
        return scan
    except Exception as e:
        logging.error(f"Error retrieving scan: {e}")
        raise

async def update_scan(scan_id: str, update_data: dict) -> dict | None:
    """
    Update a scan's details.
    
    Args:
        scan_id (str): Unique scan identifier
        update_data (dict): Fields to update
    
    Returns:
        dict | None: Updated scan or None if not found
    """
    try:
        # Add updated_at timestamp
        update_data['updated_at'] = datetime.utcnow()
        
        # Update scan
        result = await database.db['scans'].update_one(
            {'_id': ObjectId(scan_id)}, 
            {'$set': update_data}
        )
        
        # Retrieve updated scan
        if result.modified_count > 0:
            updated_scan = await database.db['scans'].find_one({'_id': ObjectId(scan_id)})
            
            # Convert ObjectId to string
            updated_scan['_id'] = str(updated_scan['_id'])
            
            return updated_scan
        
        return None
    except Exception as e:
        logging.error(f"Error updating scan: {e}")
        raise

async def list_scans(skip: int = 0, limit: int = 100, status: Optional[str] = None) -> list[dict]:
    """
    List scans with optional filtering and pagination.
    
    Args:
        skip (int): Number of scans to skip for pagination
        limit (int): Maximum number of scans to return
        status (Optional[str]): Filter by scan status
    
    Returns:
        list[dict]: List of scans
    """
    try:
        # Prepare query
        query = {}
        if status:
            query['status'] = status
        
        # Find scans with pagination
        cursor = database.db['scans'].find(query).skip(skip).limit(limit)
        
        # Convert results
        scans = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for scan in scans:
            scan['_id'] = str(scan['_id'])
        
        return scans
    except Exception as e:
        logging.error(f"Error listing scans: {e}")
        raise

# Lead CRUD Methods
async def create_lead(lead_data: dict) -> dict:
    """
    Insert a new lead into the database.
    
    Args:
        lead_data (dict): Lead data to be inserted
    
    Returns:
        dict: Inserted lead with _id
    """
    try:
        # Ensure created_at is set if not provided
        if 'created_at' not in lead_data:
            lead_data['created_at'] = datetime.utcnow()
        
        # Insert lead into database
        result = await database.db['leads'].insert_one(lead_data)
        
        # Retrieve and return the inserted lead
        lead = await database.db['leads'].find_one({'_id': result.inserted_id})
        
        # Convert ObjectId to string
        lead['_id'] = str(lead['_id'])
        
        return lead
    except Exception as e:
        logging.error(f"Error creating lead: {e}")
        raise

async def get_lead_by_id(lead_id: str) -> dict | None:
    """
    Retrieve a lead by its ID.
    
    Args:
        lead_id (str): Unique lead identifier
    
    Returns:
        dict | None: Lead details or None if not found
    """
    try:
        # Find lead by ID
        lead = await database.db['leads'].find_one({'_id': ObjectId(lead_id)})
        
        if lead:
            # Convert ObjectId to string
            lead['_id'] = str(lead['_id'])
        
        return lead
    except Exception as e:
        logging.error(f"Error retrieving lead: {e}")
        raise

async def find_lead_by_email(email: str) -> dict | None:
    """
    Find a lead by email address.
    
    Args:
        email (str): Email address to search for
    
    Returns:
        dict | None: Lead details or None if not found
    """
    try:
        # Find lead by email
        lead = await database.db['leads'].find_one({'email': email})
        
        if lead:
            # Convert ObjectId to string
            lead['_id'] = str(lead['_id'])
        
        return lead
    except Exception as e:
        logging.error(f"Error finding lead by email: {e}")
        raise

async def update_lead(lead_id: str, update_data: dict) -> dict | None:
    """
    Update a lead's details.
    
    Args:
        lead_id (str): Unique lead identifier
        update_data (dict): Fields to update
    
    Returns:
        dict | None: Updated lead or None if not found
    """
    try:
        # Add updated_at timestamp
        update_data['updated_at'] = datetime.utcnow()
        
        # Update lead
        result = await database.db['leads'].update_one(
            {'_id': ObjectId(lead_id)}, 
            {'$set': update_data}
        )
        
        # Retrieve updated lead
        if result.modified_count > 0:
            updated_lead = await database.db['leads'].find_one({'_id': ObjectId(lead_id)})
            
            # Convert ObjectId to string
            updated_lead['_id'] = str(updated_lead['_id'])
            
            return updated_lead
        
        return None
    except Exception as e:
        logging.error(f"Error updating lead: {e}")
        raise

async def list_leads(skip: int = 0, limit: int = 100, status: Optional[str] = None) -> list[dict]:
    """
    List leads with optional filtering and pagination.
    
    Args:
        skip (int): Number of leads to skip for pagination
        limit (int): Maximum number of leads to return
        status (Optional[str]): Filter by lead status
    
    Returns:
        list[dict]: List of leads
    """
    try:
        # Prepare query
        query = {}
        if status:
            query['status'] = status
        
        # Find leads with pagination
        cursor = database.db['leads'].find(query).skip(skip).limit(limit)
        
        # Convert results
        leads = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for lead in leads:
            lead['_id'] = str(lead['_id'])
        
        return leads
    except Exception as e:
        logging.error(f"Error listing leads: {e}")
        raise

# Restaurant CRUD Methods
async def get_restaurant_by_id(restaurant_id: str) -> dict | None:
    """
    Retrieve a restaurant by its ID.
    
    Args:
        restaurant_id (str): Unique restaurant identifier
    
    Returns:
        dict | None: Restaurant details or None if not found
    """
    try:
        # Find restaurant by ID
        restaurant = await database.db['restaurants'].find_one({'_id': ObjectId(restaurant_id)})
        
        if restaurant:
            # Convert ObjectId to string
            restaurant['_id'] = str(restaurant['_id'])
        
        return restaurant
    except Exception as e:
        logging.error(f"Error retrieving restaurant: {e}")
        raise

async def create_restaurant(restaurant_data: dict) -> dict:
    """
    Insert a new restaurant into the database.
    
    Args:
        restaurant_data (dict): Restaurant data to be inserted
    
    Returns:
        dict: Inserted restaurant with _id
    """
    try:
        # Ensure created_at is set if not provided
        if 'created_at' not in restaurant_data:
            restaurant_data['created_at'] = datetime.utcnow()
        
        # Insert restaurant into database
        result = await database.db['restaurants'].insert_one(restaurant_data)
        
        # Retrieve and return the inserted restaurant
        restaurant = await database.db['restaurants'].find_one({'_id': result.inserted_id})
        
        # Convert ObjectId to string
        restaurant['_id'] = str(restaurant['_id'])
        
        return restaurant
    except Exception as e:
        logging.error(f"Error creating restaurant: {e}")
        raise

async def find_restaurant_by_place_id(place_id: str) -> dict | None:
    """
    Find a restaurant by its Google Place ID.
    
    Args:
        place_id (str): Google Place ID to search for
    
    Returns:
        dict | None: Restaurant details or None if not found
    """
    try:
        # Find restaurant by Google Place ID
        restaurant = await database.db['restaurants'].find_one({'place_id': place_id})
        
        if restaurant:
            # Convert ObjectId to string
            restaurant['_id'] = str(restaurant['_id'])
        
        return restaurant
    except Exception as e:
        logging.error(f"Error finding restaurant by Place ID: {e}")
        raise