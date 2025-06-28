"use client"

/**
 * Main App Component
 * Natural Language Cross-Platform Data Query RAG Agent
 *
 * This is the root component that handles routing and global state management
 */

import { useState, useEffect } from "react"
import "./App.css"

// Import our custom components
import HomePage from "./pages/HomePage"
import { QueryProvider } from "./contexts/QueryContext"
import Header from "./components/Header"
import Footer from "./components/Footer"
import LoadingSpinner from "./components/LoadingSpinner"
import ErrorBoundary from "./components/ErrorBoundary"

// Import API service for health check
import { apiService } from "./services/apiService"

function App() {
  const [isBackendHealthy, setIsBackendHealthy] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [backendError, setBackendError] = useState(null)

  useEffect(() => {
    /**
     * Check backend health on app startup
     * This ensures we have a working connection to our FastAPI backend
     */
    const checkBackendHealth = async () => {
      try {
        setIsLoading(true)
        const response = await apiService.checkHealth()

        if (response.status === "healthy") {
          setIsBackendHealthy(true)
          console.log("✅ Backend connection established")
        } else {
          throw new Error("Backend returned unhealthy status")
        }
      } catch (error) {
        console.error("❌ Backend health check failed:", error)
        setBackendError(error.message)
        setIsBackendHealthy(false)
      } finally {
        setIsLoading(false)
      }
    }

    checkBackendHealth()
  }, [])

  // Show loading spinner while checking backend health
  if (isLoading) {
    return (
      <div className="app-loading">
        <LoadingSpinner message="Connecting to AI Query System..." />
      </div>
    )
  }

  // Show error message if backend is not available
  if (!isBackendHealthy) {
    return (
      <div className="app-error">
        <div className="error-container">
          <h1>🚨 System Unavailable</h1>
          <p>Unable to connect to the AI Query System backend.</p>
          <p className="error-details">{backendError}</p>
          <div className="error-actions">
            <button onClick={() => window.location.reload()} className="retry-button">
              🔄 Retry Connection
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Main app render when everything is working
  return (
    <ErrorBoundary>
      <QueryProvider>
        <div className="App">
          <Header />
          <main className="main-content">
            <HomePage />
          </main>
          <Footer />
        </div>
      </QueryProvider>
    </ErrorBoundary>
  )
}

export default App
