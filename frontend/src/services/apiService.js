/**
 * API Service
 * Handles all communication with the FastAPI backend
 */

import axios from "axios"

// Base configuration for API calls
const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000"

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 second timeout
  headers: {
    "Content-Type": "application/json",
  },
})

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error("❌ API Request Error:", error)
    return Promise.reject(error)
  },
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error("❌ API Response Error:", error.response?.data || error.message)

    // Handle specific error cases for better UX
    if (error.code === "ECONNABORTED") {
      error.userMessage = "Request timed out. The AI system might be processing a complex query."
    } else if (error.response?.status === 500) {
      error.userMessage = "Internal server error. Please try again or contact support."
    } else if (error.response?.status === 404) {
      error.userMessage = "API endpoint not found. Please check your connection."
    } else if (!error.response) {
      error.userMessage = "Unable to connect to the server. Please check your internet connection."
    } else {
      error.userMessage = error.response?.data?.detail || "An unexpected error occurred."
    }

    return Promise.reject(error)
  },
)

export const apiService = {
  /**
   * Health check endpoint
   * Verifies backend connectivity and service status
   */
  async checkHealth() {
    try {
      const response = await apiClient.get("/health")
      return response.data
    } catch (error) {
      throw new Error(`Health check failed: ${error.userMessage || error.message}`)
    }
  },

  /**
   * Process a natural language query
   * Main endpoint for AI-powered data queries
   */
  async processQuery(query, userId = "default_user") {
    try {
      const response = await apiClient.post("/api/v1/query", {
        query: query.trim(),
        user_id: userId,
      })

      return response.data
    } catch (error) {
      throw new Error(error.userMessage || "Failed to process query")
    }
  },

  /**
   * Get example queries for user guidance
   */
  async getQueryExamples() {
    try {
      const response = await apiClient.get("/api/v1/query/examples")
      return response.data
    } catch (error) {
      console.warn("⚠️ Failed to fetch examples, using fallback")
      // Return fallback examples if API fails
      return {
        success: true,
        examples: [
          {
            category: "Portfolio Analysis",
            queries: [
              "What are the top five portfolios of our wealth members?",
              "Show me the portfolio breakdown by investment type",
              "Which clients have the highest portfolio values?",
            ],
          },
          {
            category: "Relationship Manager Insights",
            queries: [
              "Breakup of portfolio values by relationship manager",
              "Who are the top relationship managers?",
              "Show me performance by relationship manager",
            ],
          },
          {
            category: "Client Information",
            queries: [
              "List all clients with conservative risk appetite",
              "Which clients hold the most equity investments?",
              "Show me clients from Mumbai",
            ],
          },
        ],
      }
    }
  },

  /**
   * Get system statistics
   */
  async getStats() {
    try {
      const response = await apiClient.get("/api/v1/query/stats")
      return response.data
    } catch (error) {
      console.warn("⚠️ Failed to fetch stats")
      return {
        success: false,
        stats: {
          total_clients: "N/A",
          active_portfolios: "N/A",
          total_portfolio_value: "N/A",
          relationship_managers: "N/A",
        },
      }
    }
  },
}
