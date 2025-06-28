"""
Query API Routes
Handles HTTP requests for natural language queries
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Dict, Any
import logging

from services.query_processor import QueryProcessor

logger = logging.getLogger(__name__)

router = APIRouter()

class QueryRequest(BaseModel):
    """Request model for user queries"""
    query: str
    user_id: str = "default_user"

class QueryResponse(BaseModel):
    """Response model for query results"""
    success: bool
    text_response: str
    table_data: Dict[str, Any] = None
    chart_data: Dict[str, Any] = None
    error_message: str = None

# Initialize query processor
query_processor = QueryProcessor()

@router.post("/query", response_model=QueryResponse)
async def process_natural_language_query(request: QueryRequest, app_request: Request):
    """
    Process a natural language query and return structured response
    
    Args:
        request: QueryRequest containing the user's natural language query
        app_request: FastAPI request object to access app state
    
    Returns:
        QueryResponse with text, table, and chart data
    """
    try:
        logger.info(f"📥 Received query from user {request.user_id}: {request.query}")
        
        # Get database connections from app state
        mongodb = app_request.app.state.mongodb
        mysql = app_request.app.state.mysql
        
        # Validate query
        if not request.query or len(request.query.strip()) < 3:
            raise HTTPException(
                status_code=400, 
                detail="Query must be at least 3 characters long"
            )
        
        # Process the query
        result = await query_processor.process_query(
            user_query=request.query,
            mongodb=mongodb,
            mysql=mysql
        )
        
        # Check for errors in processing
        if result.get("error", False):
            logger.error(f"❌ Query processing failed: {result.get('message', 'Unknown error')}")
            return QueryResponse(
                success=False,
                text_response="I'm sorry, I couldn't process your query at this time.",
                error_message=result.get("message", "Processing error")
            )
        
        # Return successful response
        logger.info(f"✅ Query processed successfully for user {request.user_id}")
        return QueryResponse(
            success=True,
            text_response=result.get("text_response", "Query processed successfully"),
            table_data=result.get("table_data"),
            chart_data=result.get("chart_data")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error processing query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/query/examples")
async def get_query_examples():
    """
    Get example queries that users can try
    """
    examples = [
        {
            "category": "Portfolio Analysis",
            "queries": [
                "What are the top five portfolios of our wealth members?",
                "Show me the portfolio breakdown by investment type",
                "Which clients have the highest portfolio values?"
            ]
        },
        {
            "category": "Relationship Manager Insights",
            "queries": [
                "Breakup of portfolio values by relationship manager",
                "Who are the top relationship managers?",
                "Show me performance by relationship manager"
            ]
        },
        {
            "category": "Client Information",
            "queries": [
                "List all clients with conservative risk appetite",
                "Which clients hold the most equity investments?",
                "Show me clients from Mumbai"
            ]
        }
    ]
    
    return {
        "success": True,
        "examples": examples,
        "total_categories": len(examples)
    }

@router.get("/query/stats")
async def get_query_stats(app_request: Request):
    """
    Get basic statistics about the data
    """
    try:
        mongodb = app_request.app.state.mongodb
        mysql = app_request.app.state.mysql
        
        # Get counts from databases with proper error handling
        try:
            client_count = await mongodb.get_collection("client_profiles").count_documents({})
        except Exception as db_error:
            logger.warning(f"⚠️ Could not get client count: {db_error}")
            client_count = 0
        
        stats = {
            "total_clients": client_count,
            "active_portfolios": 25,  # This would come from actual MySQL query
            "total_portfolio_value": "₹500+ Crores",
            "relationship_managers": 5,
            "last_updated": "2024-01-15T10:30:00Z"
        }
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting stats: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "stats": {}
        }
