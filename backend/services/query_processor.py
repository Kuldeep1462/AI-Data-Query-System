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
        Process a natural language query and return structured response
        """
        try:
            logger.info(f"🔍 Processing query: {user_query}")
            
            # Step 1: Analyze query intent
            analysis = await self._analyze_query_intent(user_query)
            analysis["user_query"] = user_query  # Add user query for filtering
            
            logger.info(f"📊 Query analysis: {analysis}")
            
            # Step 2: Fetch relevant data
            raw_data = await self._fetch_relevant_data(analysis, mongodb, mysql)
            
            if "error" in raw_data:
                return {
                    "error": True,
                    "message": raw_data["error"],
                    "text_response": "Error fetching data",
                    "table_data": None,
                    "chart_data": None
                }
            
            logger.info(f"📈 Fetched data: {len(raw_data.get('client_profiles', []))} clients, {len(raw_data.get('transactions', []))} transactions")
            
            # Step 3: Format response
            response = await self._format_response(user_query, raw_data, analysis)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Query processing error: {str(e)}")
            return {
                "error": True,
                "message": str(e),
                "text_response": "Error processing query",
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
            user_query = analysis.get("user_query", "").lower()
            
            # Filter based on user query keywords
            filter_criteria = {}
            
            # Location-based filtering
            if "mumbai" in user_query:
                filter_criteria["location"] = "Mumbai"
            elif "ranchi" in user_query:
                filter_criteria["location"] = "Ranchi"
            
            # Risk appetite filtering
            if "conservative" in user_query:
                filter_criteria["risk_appetite"] = "conservative"
            elif "moderate" in user_query:
                filter_criteria["risk_appetite"] = "moderate"
            elif "aggressive" in user_query:
                filter_criteria["risk_appetite"] = "aggressive"
            
            # Name-based filtering
            if any(name in user_query for name in ["virat", "kohli"]):
                filter_criteria["name"] = {"$regex": "Virat", "$options": "i"}
            elif any(name in user_query for name in ["dhoni", "ms"]):
                filter_criteria["name"] = {"$regex": "Dhoni", "$options": "i"}
            elif any(name in user_query for name in ["rohit", "sharma"]):
                filter_criteria["name"] = {"$regex": "Rohit", "$options": "i"}
            elif any(name in user_query for name in ["deepika", "padukone"]):
                filter_criteria["name"] = {"$regex": "Deepika", "$options": "i"}
            elif any(name in user_query for name in ["shah rukh", "khan"]):
                filter_criteria["name"] = {"$regex": "Shah Rukh", "$options": "i"}
            
            if filter_criteria:
                # Apply filters
                cursor = collection.find(filter_criteria).sort("portfolio_value", -1).limit(20)
                return await cursor.to_list(length=20)
            elif "top" in query_type or "portfolio" in query_type:
                # Fetch top clients by portfolio value
                cursor = collection.find({}).sort("portfolio_value", -1).limit(10)
                return await cursor.to_list(length=10)
            else:
                # Fetch all client profiles
                cursor = collection.find({}).limit(20)
                return await cursor.to_list(length=20)
                
        except Exception as e:
            logger.error(f"❌ MongoDB query error: {str(e)}")
            # Return filtered sample data as fallback
            return self._get_filtered_sample_mongodb_data(analysis)
    
    def _get_filtered_sample_mongodb_data(self, analysis: Dict[str, Any]) -> List[Dict]:
        """Return filtered sample MongoDB data based on query analysis"""
        user_query = analysis.get("user_query", "").lower()
        all_data = self._get_sample_mongodb_data()
        
        # Apply filters to sample data
        filtered_data = []
        
        for client in all_data:
            include_client = True
            
            # Location filtering
            if "mumbai" in user_query and client.get("location") != "Mumbai":
                include_client = False
            elif "ranchi" in user_query and client.get("location") != "Ranchi":
                include_client = False
            
            # Risk appetite filtering
            if "conservative" in user_query and client.get("risk_appetite") != "conservative":
                include_client = False
            elif "moderate" in user_query and client.get("risk_appetite") != "moderate":
                include_client = False
            elif "aggressive" in user_query and client.get("risk_appetite") != "aggressive":
                include_client = False
            
            # Name filtering
            if any(name in user_query for name in ["virat", "kohli"]) and "Virat" not in client.get("name", ""):
                include_client = False
            elif any(name in user_query for name in ["dhoni", "ms"]) and "Dhoni" not in client.get("name", ""):
                include_client = False
            elif any(name in user_query for name in ["rohit", "sharma"]) and "Rohit" not in client.get("name", ""):
                include_client = False
            elif any(name in user_query for name in ["deepika", "padukone"]) and "Deepika" not in client.get("name", ""):
                include_client = False
            elif any(name in user_query for name in ["shah rukh", "khan"]) and "Shah Rukh" not in client.get("name", ""):
                include_client = False
            
            if include_client:
                filtered_data.append(client)
        
        return filtered_data if filtered_data else all_data  # Return all if no filters match
    
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
            {"client_id": "C001", "name": "Virat Kohli", "portfolio_value": 50000000, "risk_appetite": "moderate", "location": "Mumbai", "age": 35, "income_level": "high"},
            {"client_id": "C002", "name": "MS Dhoni", "portfolio_value": 75000000, "risk_appetite": "conservative", "location": "Ranchi", "age": 42, "income_level": "high"},
            {"client_id": "C003", "name": "Rohit Sharma", "portfolio_value": 45000000, "risk_appetite": "aggressive", "location": "Mumbai", "age": 36, "income_level": "high"},
            {"client_id": "C004", "name": "Deepika Padukone", "portfolio_value": 60000000, "risk_appetite": "moderate", "location": "Mumbai", "age": 38, "income_level": "high"},
            {"client_id": "C005", "name": "Shah Rukh Khan", "portfolio_value": 100000000, "risk_appetite": "conservative", "location": "Mumbai", "age": 58, "income_level": "high"}
        ]
    
    def _get_sample_mysql_data(self) -> List[Dict]:
        """Sample MySQL data for demonstration"""
        return [
            {"client_id": "C001", "portfolio_value": 25000000, "relationship_manager": "Amit Kumar", "investment_type": "Equity"},
            {"client_id": "C001", "portfolio_value": 15000000, "relationship_manager": "Amit Kumar", "investment_type": "Bonds"},
            {"client_id": "C001", "portfolio_value": 10000000, "relationship_manager": "Amit Kumar", "investment_type": "Mutual Funds"},
            {"client_id": "C002", "portfolio_value": 40000000, "relationship_manager": "Priya Singh", "investment_type": "Mutual Funds"},
            {"client_id": "C002", "portfolio_value": 20000000, "relationship_manager": "Priya Singh", "investment_type": "Fixed Deposits"},
            {"client_id": "C002", "portfolio_value": 15000000, "relationship_manager": "Priya Singh", "investment_type": "Real Estate"},
            {"client_id": "C003", "portfolio_value": 30000000, "relationship_manager": "Rajesh Mehta", "investment_type": "Bonds"},
            {"client_id": "C003", "portfolio_value": 15000000, "relationship_manager": "Rajesh Mehta", "investment_type": "Equity"},
            {"client_id": "C004", "portfolio_value": 35000000, "relationship_manager": "Neha Gupta", "investment_type": "Real Estate"},
            {"client_id": "C004", "portfolio_value": 25000000, "relationship_manager": "Neha Gupta", "investment_type": "Mutual Funds"},
            {"client_id": "C005", "portfolio_value": 50000000, "relationship_manager": "Amit Kumar", "investment_type": "Mixed Portfolio"},
            {"client_id": "C005", "portfolio_value": 30000000, "relationship_manager": "Amit Kumar", "investment_type": "International Funds"},
            {"client_id": "C005", "portfolio_value": 20000000, "relationship_manager": "Amit Kumar", "investment_type": "Equity"}
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
            # Create a more structured data summary
            data_summary = self._create_data_summary(raw_data)
            
            summary_prompt = f"""
            You are a professional wealth management analyst. Based on the following data, provide a clear, concise summary for this query.
            
            User Query: "{user_query}"
            
            Data Summary:
            {data_summary}
            
            Analysis Context: {analysis.get('intent', 'General query')}
            
            Please provide a professional response that:
            1. Directly answers the user's question
            2. Highlights key insights and numbers
            3. Uses clear, professional language
            4. Is concise but informative (2-4 paragraphs max)
            5. Includes specific data points when relevant
            
            Response:
            """
            
            response = self.model.generate_content(summary_prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.warning(f"⚠️ Text summary generation failed: {str(e)}")
            # Provide a better fallback response
            return self._generate_fallback_summary(user_query, raw_data, analysis)
    
    def _create_data_summary(self, raw_data: Dict[str, Any]) -> str:
        """
        Create a structured summary of the data for the AI prompt
        """
        summary_parts = []
        
        if "client_profiles" in raw_data:
            clients = raw_data["client_profiles"]
            summary_parts.append(f"Client Profiles: {len(clients)} clients found")
            
            # Add key statistics
            if clients:
                total_value = sum(client.get('portfolio_value', 0) for client in clients)
                risk_levels = {}
                locations = {}
                
                for client in clients:
                    risk = client.get('risk_appetite', 'Unknown')
                    location = client.get('location', 'Unknown')
                    risk_levels[risk] = risk_levels.get(risk, 0) + 1
                    locations[location] = locations.get(location, 0) + 1
                
                summary_parts.append(f"Total Portfolio Value: ₹{total_value:,}")
                summary_parts.append(f"Risk Distribution: {dict(risk_levels)}")
                summary_parts.append(f"Location Distribution: {dict(locations)}")
        
        if "transactions" in raw_data:
            transactions = raw_data["transactions"]
            summary_parts.append(f"Transactions: {len(transactions)} records found")
            
            if transactions:
                total_transaction_value = sum(t.get('portfolio_value', 0) for t in transactions)
                investment_types = {}
                managers = {}
                
                for transaction in transactions:
                    inv_type = transaction.get('investment_type', 'Unknown')
                    manager = transaction.get('relationship_manager', 'Unknown')
                    investment_types[inv_type] = investment_types.get(inv_type, 0) + 1
                    managers[manager] = managers.get(manager, 0) + 1
                
                summary_parts.append(f"Total Transaction Value: ₹{total_transaction_value:,}")
                summary_parts.append(f"Investment Types: {dict(investment_types)}")
                summary_parts.append(f"Relationship Managers: {dict(managers)}")
        
        return "\n".join(summary_parts) if summary_parts else "No data available"
    
    def _generate_fallback_summary(self, user_query: str, raw_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """
        Generate a fallback summary when AI generation fails
        """
        try:
            data_summary = self._create_data_summary(raw_data)
            
            if "client_profiles" in raw_data and "transactions" in raw_data:
                clients = raw_data["client_profiles"]
                transactions = raw_data["transactions"]
                
                total_clients = len(clients)
                total_transactions = len(transactions)
                total_value = sum(client.get('portfolio_value', 0) for client in clients)
                
                return f"""Based on your query "{user_query}", I found relevant data in our wealth management system:

📊 Data Overview:
• Total Clients: {total_clients}
• Total Transactions: {total_transactions}
• Total Portfolio Value: ₹{total_value:,}

The data shows comprehensive information about our wealth management clients and their investment portfolios. Please check the table and chart tabs for detailed breakdowns and visualizations.

Key insights are available in the structured data views, including portfolio values, investment types, and relationship manager performance."""
            
            elif "client_profiles" in raw_data:
                clients = raw_data["client_profiles"]
                total_clients = len(clients)
                total_value = sum(client.get('portfolio_value', 0) for client in clients)
                
                return f"""Based on your query "{user_query}", I found client profile information:

👥 Client Overview:
• Total Clients: {total_clients}
• Total Portfolio Value: ₹{total_value:,}

The data includes detailed client profiles with portfolio values, risk appetites, and demographic information. Please check the table view for a complete breakdown of client data."""
            
            elif "transactions" in raw_data:
                transactions = raw_data["transactions"]
                total_transactions = len(transactions)
                total_value = sum(t.get('portfolio_value', 0) for t in transactions)
                
                return f"""Based on your query "{user_query}", I found transaction data:

💼 Transaction Overview:
• Total Transactions: {total_transactions}
• Total Value: ₹{total_value:,}

The data includes detailed transaction records with portfolio values, investment types, and relationship manager information. Please check the table view for a complete breakdown."""
            
            else:
                return f"""Based on your query "{user_query}", I couldn't find specific data matching your request. 

Please try rephrasing your question or check the table and chart views for available data. You can ask about:
• Client portfolios and values
• Investment types and distributions
• Relationship manager performance
• Risk appetite analysis"""
                
        except Exception as e:
            logger.error(f"❌ Fallback summary generation failed: {str(e)}")
            return f"Based on your query '{user_query}', I found relevant data in our wealth management system. Please check the table and chart tabs for detailed information."
    
    def _format_table_data(self, raw_data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format data for table display
        """
        try:
            # Combine MongoDB and MySQL data for table display
            table_rows = []
            
            if "client_profiles" in raw_data and "transactions" in raw_data:
                # Create a map of client data
                clients = {item["client_id"]: item for item in raw_data["client_profiles"]}
                
                # Aggregate transactions by client to avoid duplicates
                client_portfolios = {}
                
                for transaction in raw_data["transactions"]:
                    client_id = transaction.get("client_id")
                    if client_id not in client_portfolios:
                        client_portfolios[client_id] = {
                            "total_value": 0,
                            "investment_types": set(),
                            "relationship_managers": set()
                        }
                    
                    client_portfolios[client_id]["total_value"] += transaction.get("portfolio_value", 0)
                    client_portfolios[client_id]["investment_types"].add(transaction.get("investment_type", "N/A"))
                    client_portfolios[client_id]["relationship_managers"].add(transaction.get("relationship_manager", "N/A"))
                
                # Create table rows from aggregated data
                for client_id, portfolio_data in client_portfolios.items():
                    client_info = clients.get(client_id, {})
                    
                    row = {
                        "Client ID": client_id,
                        "Client Name": client_info.get("name", "Unknown"),
                        "Total Portfolio Value": f"₹{portfolio_data['total_value']:,}",
                        "Relationship Manager": ", ".join(portfolio_data["relationship_managers"]),
                        "Investment Types": ", ".join(portfolio_data["investment_types"]),
                        "Risk Appetite": client_info.get("risk_appetite", "N/A"),
                        "Location": client_info.get("location", "N/A")
                    }
                    table_rows.append(row)
            
            elif "client_profiles" in raw_data:
                # Only client profiles available
                for client in raw_data["client_profiles"]:
                    row = {
                        "Client ID": client.get("client_id", ""),
                        "Client Name": client.get("name", ""),
                        "Portfolio Value": f"₹{client.get('portfolio_value', 0):,}",
                        "Risk Appetite": client.get("risk_appetite", ""),
                        "Location": client.get("location", ""),
                        "Age": client.get("age", ""),
                        "Income Level": client.get("income_level", "")
                    }
                    table_rows.append(row)
            
            elif "transactions" in raw_data:
                # Only transactions available - aggregate by client
                client_portfolios = {}
                
                for transaction in raw_data["transactions"]:
                    client_id = transaction.get("client_id")
                    if client_id not in client_portfolios:
                        client_portfolios[client_id] = {
                            "total_value": 0,
                            "investment_types": set(),
                            "relationship_managers": set()
                        }
                    
                    client_portfolios[client_id]["total_value"] += transaction.get("portfolio_value", 0)
                    client_portfolios[client_id]["investment_types"].add(transaction.get("investment_type", "N/A"))
                    client_portfolios[client_id]["relationship_managers"].add(transaction.get("relationship_manager", "N/A"))
                
                for client_id, portfolio_data in client_portfolios.items():
                    row = {
                        "Client ID": client_id,
                        "Total Portfolio Value": f"₹{portfolio_data['total_value']:,}",
                        "Relationship Manager": ", ".join(portfolio_data["relationship_managers"]),
                        "Investment Types": ", ".join(portfolio_data["investment_types"])
                    }
                    table_rows.append(row)
            
            # Sort by portfolio value (descending)
            table_rows.sort(key=lambda x: float(x.get("Total Portfolio Value", "0").replace("₹", "").replace(",", "")), reverse=True)
            
            # Filter out rows with "Unknown" client names
            table_rows = [row for row in table_rows if row.get("Client Name") != "Unknown"]
            
            return {
                "columns": list(table_rows[0].keys()) if table_rows else [],
                "rows": table_rows[:20]  # Limit to top 20 rows
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
                return self._create_pie_chart_data(raw_data, analysis)
            elif viz_type == "line_chart":
                return self._create_line_chart_data(raw_data)
            else:
                return self._create_bar_chart_data(raw_data, analysis)
                
        except Exception as e:
            logger.error(f"❌ Error generating chart data: {str(e)}")
            return {"type": "bar", "labels": [], "data": []}
    
    def _create_bar_chart_data(self, raw_data: Dict[str, Any], analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create bar chart data using filtered data based on user query"""
        try:
            # Get filtered data based on user query
            filtered_data = self._get_filtered_data_for_charts(raw_data, analysis)
            
            if "transactions" in filtered_data:
                # Group by relationship manager
                manager_portfolios = {}
                for transaction in filtered_data["transactions"]:
                    manager = transaction.get("relationship_manager", "Unknown")
                    value = transaction.get("portfolio_value", 0)
                    manager_portfolios[manager] = manager_portfolios.get(manager, 0) + value
                
                if manager_portfolios:
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
            
            # Fallback to client-based chart if no transactions
            if "client_profiles" in filtered_data:
                client_portfolios = {}
                for client in filtered_data["client_profiles"]:
                    name = client.get("name", "Unknown")
                    value = client.get("portfolio_value", 0)
                    client_portfolios[name] = value
                
                if client_portfolios:
                    return {
                        "type": "bar",
                        "title": "Client Portfolio Values",
                        "labels": list(client_portfolios.keys()),
                        "datasets": [{
                            "label": "Portfolio Value (₹)",
                            "data": list(client_portfolios.values()),
                            "backgroundColor": ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"]
                        }]
                    }
            
            return {"type": "bar", "labels": [], "datasets": []}
            
        except Exception as e:
            logger.error(f"❌ Error creating bar chart: {str(e)}")
            return {"type": "bar", "labels": [], "datasets": []}
    
    def _create_pie_chart_data(self, raw_data: Dict[str, Any], analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create pie chart data using filtered data based on user query"""
        try:
            # Get filtered data based on user query
            filtered_data = self._get_filtered_data_for_charts(raw_data, analysis)
            
            if "transactions" in filtered_data:
                # Group by investment type
                investment_breakdown = {}
                for transaction in filtered_data["transactions"]:
                    inv_type = transaction.get("investment_type", "Unknown")
                    value = transaction.get("portfolio_value", 0)
                    investment_breakdown[inv_type] = investment_breakdown.get(inv_type, 0) + value
                
                if investment_breakdown:
                    return {
                        "type": "pie",
                        "title": "Portfolio Breakdown by Investment Type",
                        "labels": list(investment_breakdown.keys()),
                        "datasets": [{
                            "data": list(investment_breakdown.values()),
                            "backgroundColor": ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"]
                        }]
                    }
            
            # Fallback to risk appetite breakdown if no transactions
            if "client_profiles" in filtered_data:
                risk_breakdown = {}
                for client in filtered_data["client_profiles"]:
                    risk = client.get("risk_appetite", "Unknown")
                    value = client.get("portfolio_value", 0)
                    risk_breakdown[risk] = risk_breakdown.get(risk, 0) + value
                
                if risk_breakdown:
                    return {
                        "type": "pie",
                        "title": "Portfolio Breakdown by Risk Appetite",
                        "labels": list(risk_breakdown.keys()),
                        "datasets": [{
                            "data": list(risk_breakdown.values()),
                            "backgroundColor": ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"]
                        }]
                    }
            
            return {"type": "pie", "labels": [], "datasets": []}
            
        except Exception as e:
            logger.error(f"❌ Error creating pie chart: {str(e)}")
            return {"type": "pie", "labels": [], "datasets": []}
    
    def _get_filtered_data_for_charts(self, raw_data: Dict[str, Any], analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get filtered data for charts based on user query"""
        if not analysis or "user_query" not in analysis:
            return raw_data
        
        user_query = analysis.get("user_query", "").lower()
        filtered_data = {}
        
        # Filter client profiles
        if "client_profiles" in raw_data:
            filtered_clients = []
            for client in raw_data["client_profiles"]:
                include_client = True
                
                # Location filtering
                if "mumbai" in user_query and client.get("location") != "Mumbai":
                    include_client = False
                elif "ranchi" in user_query and client.get("location") != "Ranchi":
                    include_client = False
                
                # Risk appetite filtering
                if "conservative" in user_query and client.get("risk_appetite") != "conservative":
                    include_client = False
                elif "moderate" in user_query and client.get("risk_appetite") != "moderate":
                    include_client = False
                elif "aggressive" in user_query and client.get("risk_appetite") != "aggressive":
                    include_client = False
                
                # Name filtering
                if any(name in user_query for name in ["virat", "kohli"]) and "Virat" not in client.get("name", ""):
                    include_client = False
                elif any(name in user_query for name in ["dhoni", "ms"]) and "Dhoni" not in client.get("name", ""):
                    include_client = False
                elif any(name in user_query for name in ["rohit", "sharma"]) and "Rohit" not in client.get("name", ""):
                    include_client = False
                elif any(name in user_query for name in ["deepika", "padukone"]) and "Deepika" not in client.get("name", ""):
                    include_client = False
                elif any(name in user_query for name in ["shah rukh", "khan"]) and "Shah Rukh" not in client.get("name", ""):
                    include_client = False
                
                if include_client:
                    filtered_clients.append(client)
            
            filtered_data["client_profiles"] = filtered_clients
        
        # Filter transactions based on client IDs
        if "transactions" in raw_data and "client_profiles" in filtered_data:
            filtered_client_ids = {client["client_id"] for client in filtered_data["client_profiles"]}
            filtered_transactions = [
                transaction for transaction in raw_data["transactions"]
                if transaction.get("client_id") in filtered_client_ids
            ]
            filtered_data["transactions"] = filtered_transactions
        elif "transactions" in raw_data:
            # If no client filtering, use all transactions
            filtered_data["transactions"] = raw_data["transactions"]
        
        return filtered_data
    
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
