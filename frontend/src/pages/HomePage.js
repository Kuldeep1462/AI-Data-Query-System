"use client"

/**
 * Home Page Component
 * Main interface for the AI Data Query System
 */

import { useState, useEffect } from "react"
import { useQuery } from "../contexts/QueryContext"
import { apiService } from "../services/apiService"

// Import our custom components
import QueryInput from "../components/QueryInput"
import OutputTabs from "../components/OutputTabs"
import ExampleQueries from "../components/ExampleQueries"
import StatsPanel from "../components/StatsPanel"
import QueryHistory from "../components/QueryHistory"

const HomePage = () => {
  const {
    currentQuery,
    isLoading,
    results,
    error,
    setQuery,
    setLoading,
    setResults,
    setError,
    addToHistory,
    clearResults,
  } = useQuery()

  const [examples, setExamples] = useState([])
  const [stats, setStats] = useState(null)

  useEffect(() => {
    /**
     * Load initial data when component mounts
     * This includes example queries and system statistics
     */
    const loadInitialData = async () => {
      try {
        // Load examples and stats in parallel
        const [examplesResponse, statsResponse] = await Promise.all([
          apiService.getQueryExamples(),
          apiService.getStats(),
        ])

        if (examplesResponse.success) {
          setExamples(examplesResponse.examples)
        }

        if (statsResponse.success) {
          setStats(statsResponse.stats)
        }
      } catch (error) {
        console.warn("⚠️ Failed to load initial data:", error.message)
      }
    }

    loadInitialData()
  }, [])

  const handleQuerySubmit = async (query) => {
    if (!query.trim()) {
      setError("Please enter a query")
      return
    }

    try {
      setLoading(true)
      setError(null)
      setQuery(query)

      console.log("🔍 Processing query:", query)
      const response = await apiService.processQuery(query)

      if (response.success) {
        setResults({
          textResponse: response.text_response,
          tableData: response.table_data,
          chartData: response.chart_data,
          timestamp: new Date().toISOString(),
        })

        // Add to history
        addToHistory({
          query,
          timestamp: new Date().toISOString(),
          success: true,
        })

        console.log("✅ Query processed successfully")
      } else {
        throw new Error(response.error_message || "Query processing failed")
      }
    } catch (error) {
      console.error("❌ Query processing error:", error)
      setError(error.message)

      // Add failed query to history
      addToHistory({
        query,
        timestamp: new Date().toISOString(),
        success: false,
        error: error.message,
      })
    }
  }

  const handleExampleClick = (exampleQuery) => {
    setQuery(exampleQuery)
    handleQuerySubmit(exampleQuery)
  }

  const handleClearResults = () => {
    clearResults()
  }

  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">🤖 AI Data Query System</h1>
          <p className="hero-subtitle">
            Ask questions about your wealth management data in plain English. Get instant insights with AI-powered
            analysis.
          </p>

          {stats && <StatsPanel stats={stats} />}
        </div>
      </section>

      {/* Main Query Interface */}
      <section className="query-section">
        <div className="query-container">
          <QueryInput
            onSubmit={handleQuerySubmit}
            isLoading={isLoading}
            currentQuery={currentQuery}
            onQueryChange={setQuery}
          />

          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              <span className="error-text">{error}</span>
              <button onClick={() => setError(null)} className="error-dismiss" aria-label="Dismiss error">
                ✕
              </button>
            </div>
          )}

          {results && (
            <div className="results-section">
              <div className="results-header">
                <h2>Query Results</h2>
                <button onClick={handleClearResults} className="clear-button" title="Clear results">
                  🗑️ Clear
                </button>
              </div>
              <OutputTabs results={results} />
            </div>
          )}
        </div>
      </section>

      {/* Side Panel with Examples and History */}
      <aside className="side-panel">
        <div className="panel-content">
          <ExampleQueries examples={examples} onExampleClick={handleExampleClick} isLoading={isLoading} />

          <QueryHistory />
        </div>
      </aside>
    </div>
  )
}

export default HomePage
