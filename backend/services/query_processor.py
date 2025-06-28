"""
Query Processing Service
Handles natural language queries using Gemini AI and processes data from multiple sources
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gemini AI integration
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Database imports
from db.mongodb import MongoDB
from db.mysql import MySQL
from utils.graph_generator import GraphGenerator

logger = logging.getLogger(__name__)

class QueryProcessor:
    """
    Advanced query processor that uses Gemini AI to understand natural language
    and convert it into database queries across MongoDB and MySQL
    """
    
    def __init__(self):
        # Configure Gemini AI from environment variables
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        
        # Initialize Gemini model
        self.model = genai.GenerativeModel(
            model_name="gemini-pro",
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
        )
        
        self.graph_generator = GraphGenerator()
        logger.info("✅ QueryProcessor initialized with Gemini AI")
    
    async def process_query(self, user_query: str, mongodb: MongoDB, mysql: MySQL) -> Dict[str, Any]:
        """
        Main method to process natural language queries
        Returns structured response with text, table, and chart data
        """
        try:
            logger.info(f"🔍 Processing query: {user_query}")
            
            # Step 1: Analyze query intent using Gemini AI
            query_analysis = await self._analyze_query_intent(user_query)
            logger.info(f"📊 Query analysis: {query_analysis}")
            
            # Step 2: Execute appropriate data retrieval based on intent
            raw_data = await self._fetch_relevant_data(query_analysis, mongodb, mysql)
            
            # Step 3: Process and format the data
            processed_response = await self._format_response(user_query, raw_data, query_analysis)
            
            return processed_response
            
        except Exception as e:
            logger.error(f"❌ Error processing query: {str(e)}")
            return {
                "error": True,
                "message": f"Sorry, I encountered an error processing your query: {str(e)}",
                "text_response": "Unable to process query at this time.",
                "table_data": None,
                "chart_data": None
            }
    
    async def _analyze_query_intent(self, user_query: str) -> Dict[str, Any]:
        """
        Use Gemini AI to understand the user's intent and determine data sources needed
        """
        analysis_prompt = f"""
        You are a smart financial data analyst. Analyze this query and determine:
        1. What type of information is being requested
        2. Which database(s) to query (MongoDB for client profiles, MySQL for transactions)
        3. What kind of visualization would be most appropriate
        4. Key entities mentioned (clients, portfolios, managers, stocks, etc.)
        
        Query: "{user_query}"
        
        Respond with a JSON object containing:
        {{
            "query_type": "portfolio_summary|top_performers|breakdown_analysis|client_info|transaction_data",
            "data_sources": ["mongodb", "mysql"],
            "visualization_type": "bar_chart|pie_chart|line_chart|table|text",
            "key_entities": ["entity1", "entity2"],
            "intent_summary": "Brief description of what user wants",
            "suggested_aggregations": ["sum", "count", "average", "group_by"]
        }}
        """
        
        try:
            response = self.model.generate_content(analysis_prompt)
            # Parse the JSON response
            analysis_text = response.text.strip()
            
            # Clean up the response to extract JSON
            if "```json" in analysis_text:
                json_start = analysis_text.find("```json") + 7
                json_end = analysis_text.find("```", json_start)
                analysis_text = analysis_text[json_start:json_end].strip()
            elif "```" in analysis_text:
                json_start = analysis_text.find("```") + 3
                json_end = analysis_text.find("```", json_start)
                analysis_text = analysis_text[json_start:json_end].strip()
            
            analysis = json.loads(analysis_text)
            return analysis
            
        except Exception as e:
            logger.warning(f"⚠️ Gemini analysis failed, using fallback: {str(e)}")
            # Fallback analysis based on keywords
            return self._fallback_query_analysis(user_query)
    
    def _fallback_query_analysis(self, user_query: str) -> Dict[str, Any]:
        """
        Fallback query analysis when Gemini AI fails
        """
        query_lower = user_query.lower()
        
        # Simple keyword-based analysis
        if any(word in query_lower for word in ["top", "best", "highest", "most"]):
            query_type = "top_performers"
            visualization_type = "bar_chart"
        elif any(word in query_lower for word in ["breakup", "breakdown", "distribution"]):
            query_type = "breakdown_analysis"
            visualization_type = "pie_chart"
        elif any(word in query_lower for word in ["portfolio", "investment"]):
            query_type = "portfolio_summary"
            visualization_type = "table"
        else:
            query_type = "client_info"
            visualization_type = "text"
        
        return {
            "query_type": query_type,
            "data_sources": ["mongodb", "mysql"],
            "visualization_type": visualization_type,
            "key_entities": [],
            "intent_summary": f"User query about {query_type}",
            "suggested_aggregations": ["count", "sum"]
        }
    
    async def _fetch_relevant_data(self, analysis: Dict[str, Any], mongodb: MongoDB, mysql: MySQL) -> Dict[str, Any]:
        """
        Fetch data from appropriate databases based on query analysis
        """
        data = {}
        
        try:
            # Fetch from MongoDB if needed (client profiles)
            if "mongodb" in analysis.get("data_sources", []):
                mongo_data = await self._fetch_mongodb_data(analysis, mongodb)
                data["client_profiles"] = mongo_data
            
            # Fetch from MySQL if needed (transactions)
            if "mysql" in analysis.get("data_sources", []):
                mysql_data = await self._fetch_mysql_data(analysis, mysql)
                data["transactions"] = mysql_data
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Error fetching data: {str(e)}")
            return {"error": str(e)}
    
    async def _fetch_mongodb_data(self, analysis: Dict[str, Any], mongodb: MongoDB) -> List[Dict]:
        """
        Fetch relevant data from MongoDB based on query analysis
        """
        try:
            # Sample queries - in production, these would be more sophisticated
            collection = mongodb.get_collection("client_profiles")
            
            query_type = analysis.get("query_type", "")
            
            if "top" in query_type or "portfolio" in query_type:
                # Fetch top clients by portfolio value
                cursor = collection.find({}).sort("portfolio_value", -1).limit(10)
                return await cursor.to_list(length=10)
            else:
                # Fetch all client profiles
                cursor = collection.find({}).limit(20)
                return await cursor.to_list(length=20)
                
        except Exception as e:
            logger.error(f"❌ MongoDB query error: {str(e)}")
            # Return sample data as fallback
            return self._get_sample_mongodb_data()
    
    async def _fetch_mysql_data(self, analysis: Dict[str, Any], mysql: MySQL) -> List[Dict]:
        """
        Fetch relevant data from MySQL based on query analysis
        """
        try:
            # Sample queries - in production, these would be more sophisticated
            query = """
            SELECT 
                client_id, 
                portfolio_value, 
                relationship_manager,
                investment_type,
                created_at
            FROM investments 
            ORDER BY portfolio_value DESC 
            LIMIT 20
            """
            
            result = await mysql.execute_query(query)
            return result
            
        except Exception as e:
            logger.error(f"❌ MySQL query error: {str(e)}")
            # Return sample data as fallback
            return self._get_sample_mysql_data()
    
    def _get_sample_mongodb_data(self) -> List[Dict]:
        """Sample MongoDB data for demonstration"""
        return [
            {"client_id": "C001", "name": "Virat Kohli", "portfolio_value": 50000000, "risk_appetite": "moderate"},
            {"client_id": "C002", "name": "MS Dhoni", "portfolio_value": 75000000, "risk_appetite": "conservative"},
            {"client_id": "C003", "name": "Rohit Sharma", "portfolio_value": 45000000, "risk_appetite": "aggressive"},
            {"client_id": "C004", "name": "Deepika Padukone", "portfolio_value": 60000000, "risk_appetite": "moderate"},
            {"client_id": "C005", "name": "Shah Rukh Khan", "portfolio_value": 100000000, "risk_appetite": "conservative"}
        ]
    
    def _get_sample_mysql_data(self) -> List[Dict]:
        """Sample MySQL data for demonstration"""
        return [
            {"client_id": "C001", "portfolio_value": 50000000, "relationship_manager": "Amit Kumar", "investment_type": "Equity"},
            {"client_id": "C002", "portfolio_value": 75000000, "relationship_manager": "Priya Singh", "investment_type": "Mutual Funds"},
            {"client_id": "C003", "portfolio_value": 45000000, "relationship_manager": "Rajesh Mehta", "investment_type": "Bonds"},
            {"client_id": "C004", "portfolio_value": 60000000, "relationship_manager": "Neha Gupta", "investment_type": "Real Estate"},
            {"client_id": "C005", "portfolio_value": 100000000, "relationship_manager": "Amit Kumar", "investment_type": "Mixed Portfolio"}
        ]
    
    async def _format_response(self, user_query: str, raw_data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the response with text summary, table data, and chart data
        """
        try:
            # Generate text response using Gemini AI
            text_response = await self._generate_text_summary(user_query, raw_data, analysis)
            
            # Format table data
            table_data = self._format_table_data(raw_data, analysis)
            
            # Generate chart data
            chart_data = await self._generate_chart_data(raw_data, analysis)
            
            return {
                "error": False,
                "text_response": text_response,
                "table_data": table_data,
                "chart_data": chart_data,
                "query_analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error formatting response: {str(e)}")
            return {
                "error": True,
                "message": str(e),
                "text_response": "Error formatting response",
                "table_data": None,
                "chart_data": None
            }
    
    async def _generate_text_summary(self, user_query: str, raw_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """
        Generate a human-readable text summary using Gemini AI
        """
        try:
            summary_prompt = f"""
            Based on the following data analysis, provide a clear, professional summary for this wealth management query.
            
            Original Query: "{user_query}"
            
            Data Summary: {json.dumps(raw_data, indent=2, default=str)[:1000]}...
            
            Analysis: {analysis}
            
            Provide a concise, informative response that directly answers the user's question.
            Focus on key insights, numbers, and actionable information.
            """
            
            response = self.model.generate_content(summary_prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.warning(f"⚠️ Text summary generation failed: {str(e)}")
            return f"Based on your query '{user_query}', I found relevant data in our wealth management system. Please check the table and chart tabs for detailed information."
    
    def _format_table_data(self, raw_data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format data for table display
        """
        try:
            # Combine MongoDB and MySQL data for table display
            table_rows = []
            
            if "client_profiles" in raw_data and "transactions" in raw_data:
                # Merge client and transaction data
                clients = {item["client_id"]: item for item in raw_data["client_profiles"]}
                
                for transaction in raw_data["transactions"]:
                    client_id = transaction.get("client_id")
                    client_info = clients.get(client_id, {})
                    
                    row = {
                        "Client ID": client_id,
                        "Client Name": client_info.get("name", "Unknown"),
                        "Portfolio Value": f"₹{transaction.get('portfolio_value', 0):,}",
                        "Relationship Manager": transaction.get("relationship_manager", "N/A"),
                        "Investment Type": transaction.get("investment_type", "N/A"),
                        "Risk Appetite": client_info.get("risk_appetite", "N/A")
                    }
                    table_rows.append(row)
            
            elif "client_profiles" in raw_data:
                # Only client profiles available
                for client in raw_data["client_profiles"]:
                    row = {
                        "Client ID": client.get("client_id", ""),
                        "Client Name": client.get("name", ""),
                        "Portfolio Value": f"₹{client.get('portfolio_value', 0):,}",
                        "Risk Appetite": client.get("risk_appetite", "")
                    }
                    table_rows.append(row)
            
            return {
                "columns": list(table_rows[0].keys()) if table_rows else [],
                "rows": table_rows[:10]  # Limit to top 10 rows
            }
            
        except Exception as e:
            logger.error(f"❌ Error formatting table data: {str(e)}")
            return {"columns": [], "rows": []}
    
    async def _generate_chart_data(self, raw_data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate chart data based on the visualization type
        """
        try:
            viz_type = analysis.get("visualization_type", "bar_chart")
            
            if viz_type == "pie_chart":
                return self._create_pie_chart_data(raw_data)
            elif viz_type == "line_chart":
                return self._create_line_chart_data(raw_data)
            else:
                return self._create_bar_chart_data(raw_data)
                
        except Exception as e:
            logger.error(f"❌ Error generating chart data: {str(e)}")
            return {"type": "bar", "labels": [], "data": []}
    
    def _create_bar_chart_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create bar chart data"""
        try:
            if "transactions" in raw_data:
                # Group by relationship manager
                manager_portfolios = {}
                for transaction in raw_data["transactions"]:
                    manager = transaction.get("relationship_manager", "Unknown")
                    value = transaction.get("portfolio_value", 0)
                    manager_portfolios[manager] = manager_portfolios.get(manager, 0) + value
                
                return {
                    "type": "bar",
                    "title": "Portfolio Values by Relationship Manager",
                    "labels": list(manager_portfolios.keys()),
                    "datasets": [{
                        "label": "Portfolio Value (₹)",
                        "data": list(manager_portfolios.values()),
                        "backgroundColor": ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"]
                    }]
                }
            
            return {"type": "bar", "labels": [], "datasets": []}
            
        except Exception as e:
            logger.error(f"❌ Error creating bar chart: {str(e)}")
            return {"type": "bar", "labels": [], "datasets": []}
    
    def _create_pie_chart_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create pie chart data"""
        try:
            if "transactions" in raw_data:
                # Group by investment type
                investment_breakdown = {}
                for transaction in raw_data["transactions"]:
                    inv_type = transaction.get("investment_type", "Unknown")
                    value = transaction.get("portfolio_value", 0)
                    investment_breakdown[inv_type] = investment_breakdown.get(inv_type, 0) + value
                
                return {
                    "type": "pie",
                    "title": "Portfolio Breakdown by Investment Type",
                    "labels": list(investment_breakdown.keys()),
                    "datasets": [{
                        "data": list(investment_breakdown.values()),
                        "backgroundColor": ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"]
                    }]
                }
            
            return {"type": "pie", "labels": [], "datasets": []}
            
        except Exception as e:
            logger.error(f"❌ Error creating pie chart: {str(e)}")
            return {"type": "pie", "labels": [], "datasets": []}
    
    def _create_line_chart_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create line chart data"""
        # Placeholder for time-series data
        return {
            "type": "line",
            "title": "Portfolio Performance Over Time",
            "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
            "datasets": [{
                "label": "Portfolio Growth",
                "data": [10000000, 12000000, 11500000, 13000000, 14500000],
                "borderColor": "#36A2EB",
                "fill": False
            }]
        }
