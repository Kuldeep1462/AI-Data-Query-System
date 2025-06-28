"""
MongoDB Connection and Operations
Handles client profile data storage and retrieval
"""

import asyncio
import logging
import os
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
import pymongo
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class MongoDB:
    """
    MongoDB connection and operations handler
    Manages client profiles and wealth management data
    """
    
    def __init__(self):
        self.connection_string = os.getenv("MONGODB_URL")
        self.database_name = os.getenv("MONGODB_DATABASE", "wealth_management")
        
        if not self.connection_string:
            raise ValueError("MONGODB_URL not found in environment variables")
        
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        
    async def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.connection_string)
            
            # Test the connection
            await self.client.admin.command('ping')
            logger.info("✅ MongoDB connection established successfully")
            
            # Get database
            self.database = self.client[self.database_name]
            
            # Initialize sample data if collections are empty
            await self._initialize_sample_data()
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {str(e)}")
            raise ConnectionError(f"Could not connect to MongoDB: {str(e)}")
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("🔒 MongoDB connection closed")
    
    def get_collection(self, collection_name: str) -> AsyncIOMotorCollection:
        """Get a collection from the database"""
        if not self.database:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.database[collection_name]
    
    async def _initialize_sample_data(self):
        """Initialize sample data for demonstration"""
        try:
            client_profiles = self.get_collection("client_profiles")
            
            # Check if data already exists - properly handle the count
            try:
                count = await client_profiles.count_documents({})
                if count > 0:
                    logger.info(f"📊 Found {count} existing client profiles")
                    return
            except Exception as count_error:
                logger.warning(f"⚠️ Could not check existing data count: {count_error}")
                # Continue with sample data insertion
            
            # Insert sample client profiles
            sample_clients = [
                {
                    "client_id": "C001",
                    "name": "Virat Kohli",
                    "email": "virat.kohli@email.com",
                    "phone": "+91-9876543210",
                    "address": {
                        "street": "MG Road",
                        "city": "Mumbai",
                        "state": "Maharashtra",
                        "pincode": "400001"
                    },
                    "portfolio_value": 50000000,
                    "risk_appetite": "moderate",
                    "investment_preferences": ["equity", "mutual_funds"],
                    "relationship_manager": "Amit Kumar",
                    "onboarding_date": "2022-01-15",
                    "kyc_status": "completed",
                    "category": "sports_personality"
                },
                {
                    "client_id": "C002",
                    "name": "MS Dhoni",
                    "email": "ms.dhoni@email.com",
                    "phone": "+91-9876543211",
                    "address": {
                        "street": "Marine Drive",
                        "city": "Chennai",
                        "state": "Tamil Nadu",
                        "pincode": "600001"
                    },
                    "portfolio_value": 75000000,
                    "risk_appetite": "conservative",
                    "investment_preferences": ["bonds", "fixed_deposits"],
                    "relationship_manager": "Priya Singh",
                    "onboarding_date": "2021-08-20",
                    "kyc_status": "completed",
                    "category": "sports_personality"
                },
                {
                    "client_id": "C003",
                    "name": "Rohit Sharma",
                    "email": "rohit.sharma@email.com",
                    "phone": "+91-9876543212",
                    "address": {
                        "street": "Bandra West",
                        "city": "Mumbai",
                        "state": "Maharashtra",
                        "pincode": "400050"
                    },
                    "portfolio_value": 45000000,
                    "risk_appetite": "aggressive",
                    "investment_preferences": ["equity", "derivatives"],
                    "relationship_manager": "Rajesh Mehta",
                    "onboarding_date": "2022-03-10",
                    "kyc_status": "completed",
                    "category": "sports_personality"
                },
                {
                    "client_id": "C004",
                    "name": "Deepika Padukone",
                    "email": "deepika.padukone@email.com",
                    "phone": "+91-9876543213",
                    "address": {
                        "street": "Juhu",
                        "city": "Mumbai",
                        "state": "Maharashtra",
                        "pincode": "400049"
                    },
                    "portfolio_value": 60000000,
                    "risk_appetite": "moderate",
                    "investment_preferences": ["mutual_funds", "real_estate"],
                    "relationship_manager": "Neha Gupta",
                    "onboarding_date": "2021-11-05",
                    "kyc_status": "completed",
                    "category": "film_star"
                },
                {
                    "client_id": "C005",
                    "name": "Shah Rukh Khan",
                    "email": "srk@email.com",
                    "phone": "+91-9876543214",
                    "address": {
                        "street": "Bandstand",
                        "city": "Mumbai",
                        "state": "Maharashtra",
                        "pincode": "400050"
                    },
                    "portfolio_value": 100000000,
                    "risk_appetite": "conservative",
                    "investment_preferences": ["mixed_portfolio", "international_funds"],
                    "relationship_manager": "Amit Kumar",
                    "onboarding_date": "2020-06-15",
                    "kyc_status": "completed",
                    "category": "film_star"
                }
            ]
            
            result = await client_profiles.insert_many(sample_clients)
            logger.info(f"✅ Inserted {len(result.inserted_ids)} sample client profiles")
            
        except Exception as e:
            logger.error(f"❌ Error initializing sample data: {str(e)}")
            # Don't raise here as this is just sample data
    
    async def get_clients_by_criteria(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get clients based on specific criteria"""
        try:
            collection = self.get_collection("client_profiles")
            cursor = collection.find(criteria)
            return await cursor.to_list(length=100)
        except Exception as e:
            logger.error(f"❌ Error fetching clients: {str(e)}")
            return []
    
    async def get_top_clients_by_portfolio(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top clients by portfolio value"""
        try:
            collection = self.get_collection("client_profiles")
            cursor = collection.find({}).sort("portfolio_value", -1).limit(limit)
            return await cursor.to_list(length=limit)
        except Exception as e:
            logger.error(f"❌ Error fetching top clients: {str(e)}")
            return []
