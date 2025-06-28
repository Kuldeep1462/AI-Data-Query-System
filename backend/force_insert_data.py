"""
Force Insert Sample Data
Script to manually insert the sample client data
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def force_insert_sample_data():
    """Force insert sample client data"""
    
    connection_string = os.getenv("MONGODB_URL")
    database_name = os.getenv("MONGODB_DATABASE", "wealth_management")
    
    print(f"🔗 Connecting to MongoDB...")
    
    try:
        client = AsyncIOMotorClient(connection_string)
        await client.admin.command('ping')
        print("✅ Connected to MongoDB")
        
        db = client[database_name]
        collection = db["client_profiles"]
        
        # Check current count
        current_count = await collection.count_documents({})
        print(f"📊 Current documents in collection: {current_count}")
        
        if current_count > 0:
            print("🗑️ Clearing existing data...")
            await collection.delete_many({})
            print("✅ Existing data cleared")
        
        # Sample client data
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
        
        print(f"📝 Inserting {len(sample_clients)} sample clients...")
        result = await collection.insert_many(sample_clients)
        print(f"✅ Successfully inserted {len(result.inserted_ids)} documents")
        
        # Verify the insertion
        final_count = await collection.count_documents({})
        print(f"📊 Final document count: {final_count}")
        
        # Show sample data
        print("\n📋 Sample data preview:")
        cursor = collection.find({}).limit(3)
        async for doc in cursor:
            print(f"  - {doc['name']} (ID: {doc['client_id']}) - Portfolio: ₹{doc['portfolio_value']:,}")
        
        client.close()
        print("\n✅ Sample data insertion completed!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(force_insert_sample_data()) 