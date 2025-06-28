"""
MySQL Connection and Operations
Handles investment transaction data
"""

import asyncio
import logging
import os
from typing import List, Dict, Any, Optional
import aiomysql
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class MySQL:
    """
    MySQL connection and operations handler
    Manages investment transactions and portfolio data
    """
    
    def __init__(self):
        # Database configuration from environment variables
        self.config = {
            'host': os.getenv("MYSQL_HOST", "localhost"),
            'port': int(os.getenv("MYSQL_PORT", 3306)),
            'user': os.getenv("MYSQL_USER", "root"),
            'password': os.getenv("MYSQL_PASSWORD", "root"),
            'db': os.getenv("MYSQL_DATABASE", "wealth_portfolio"),
            'charset': os.getenv("MYSQL_CHARSET", "utf8mb4"),
            'autocommit': True
        }
        
        # Validate required environment variables
        required_vars = ["MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        self.pool: Optional[aiomysql.Pool] = None
        
    async def connect(self):
        """Establish connection pool to MySQL"""
        try:
            self.pool = await aiomysql.create_pool(
                minsize=1,
                maxsize=10,
                **self.config
            )
            logger.info("✅ MySQL connection pool established successfully")
            
            # Initialize database schema and sample data
            await self._initialize_database()
            
        except Exception as e:
            logger.error(f"❌ MySQL connection failed: {str(e)}")
            # For demo purposes, we'll continue without MySQL
            logger.warning("⚠️ Continuing without MySQL connection (using sample data)")
    
    async def close(self):
        """Close MySQL connection pool"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            logger.info("🔒 MySQL connection pool closed")
    
    async def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results"""
        if not self.pool:
            logger.warning("⚠️ MySQL not connected, returning sample data")
            return self._get_sample_transaction_data()
        
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, params)
                    result = await cursor.fetchall()
                    return list(result)
                    
        except Exception as e:
            logger.error(f"❌ MySQL query error: {str(e)}")
            return self._get_sample_transaction_data()
    
    async def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows"""
        if not self.pool:
            logger.warning("⚠️ MySQL not connected")
            return 0
        
        try:
            async with self.pool.acquire() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(query, params)
                    return cursor.rowcount
                    
        except Exception as e:
            logger.error(f"❌ MySQL update error: {str(e)}")
            return 0
    
    async def _initialize_database(self):
        """Initialize database schema and sample data"""
        if not self.pool:
            return
        
        try:
            # Create investments table
            create_table_query = """
            CREATE TABLE IF NOT EXISTS investments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                client_id VARCHAR(10) NOT NULL,
                portfolio_value BIGINT NOT NULL,
                relationship_manager VARCHAR(100) NOT NULL,
                investment_type VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_client_id (client_id),
                INDEX idx_rm (relationship_manager)
            )
            """
            
            await self.execute_update(create_table_query)
            logger.info("✅ Investments table created/verified")
            
            # Check if sample data exists
            count_query = "SELECT COUNT(*) as count FROM investments"
            result = await self.execute_query(count_query)
            
            if result and result[0]['count'] == 0:
                # Insert sample data
                await self._insert_sample_data()
            else:
                logger.info(f"📊 Found {result[0]['count'] if result else 0} existing investment records")
                
        except Exception as e:
            logger.error(f"❌ Error initializing database: {str(e)}")
    
    async def _insert_sample_data(self):
        """Insert sample investment data"""
        sample_investments = [
            ("C001", 50000000, "Amit Kumar", "Equity"),
            ("C002", 75000000, "Priya Singh", "Mutual Funds"),
            ("C003", 45000000, "Rajesh Mehta", "Bonds"),
            ("C004", 60000000, "Neha Gupta", "Real Estate"),
            ("C005", 100000000, "Amit Kumar", "Mixed Portfolio"),
            ("C001", 25000000, "Amit Kumar", "Bonds"),
            ("C002", 30000000, "Priya Singh", "Fixed Deposits"),
            ("C003", 20000000, "Rajesh Mehta", "Equity"),
            ("C004", 35000000, "Neha Gupta", "Mutual Funds"),
            ("C005", 50000000, "Amit Kumar", "International Funds")
        ]
        
        insert_query = """
        INSERT INTO investments (client_id, portfolio_value, relationship_manager, investment_type)
        VALUES (%s, %s, %s, %s)
        """
        
        for investment in sample_investments:
            await self.execute_update(insert_query, investment)
        
        logger.info(f"✅ Inserted {len(sample_investments)} sample investment records")
    
    def _get_sample_transaction_data(self) -> List[Dict[str, Any]]:
        """Return sample transaction data when MySQL is not available"""
        return [
            {"client_id": "C001", "portfolio_value": 50000000, "relationship_manager": "Amit Kumar", "investment_type": "Equity"},
            {"client_id": "C002", "portfolio_value": 75000000, "relationship_manager": "Priya Singh", "investment_type": "Mutual Funds"},
            {"client_id": "C003", "portfolio_value": 45000000, "relationship_manager": "Rajesh Mehta", "investment_type": "Bonds"},
            {"client_id": "C004", "portfolio_value": 60000000, "relationship_manager": "Neha Gupta", "investment_type": "Real Estate"},
            {"client_id": "C005", "portfolio_value": 100000000, "relationship_manager": "Amit Kumar", "investment_type": "Mixed Portfolio"},
            {"client_id": "C001", "portfolio_value": 25000000, "relationship_manager": "Amit Kumar", "investment_type": "Bonds"},
            {"client_id": "C002", "portfolio_value": 30000000, "relationship_manager": "Priya Singh", "investment_type": "Fixed Deposits"},
            {"client_id": "C003", "portfolio_value": 20000000, "relationship_manager": "Rajesh Mehta", "investment_type": "Equity"},
            {"client_id": "C004", "portfolio_value": 35000000, "relationship_manager": "Neha Gupta", "investment_type": "Mutual Funds"},
            {"client_id": "C005", "portfolio_value": 50000000, "relationship_manager": "Amit Kumar", "investment_type": "International Funds"}
        ]
    
    async def get_portfolio_summary(self) -> List[Dict[str, Any]]:
        """Get portfolio summary data"""
        query = """
        SELECT 
            client_id,
            SUM(portfolio_value) as total_value,
            relationship_manager,
            COUNT(*) as investment_count
        FROM investments 
        GROUP BY client_id, relationship_manager
        ORDER BY total_value DESC
        """
        return await self.execute_query(query)
    
    async def get_rm_performance(self) -> List[Dict[str, Any]]:
        """Get relationship manager performance"""
        query = """
        SELECT 
            relationship_manager,
            COUNT(DISTINCT client_id) as client_count,
            SUM(portfolio_value) as total_managed,
            AVG(portfolio_value) as avg_portfolio
        FROM investments 
        GROUP BY relationship_manager
        ORDER BY total_managed DESC
        """
        return await self.execute_query(query)
