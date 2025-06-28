"use client"

/**
 * Query History Component
 * Shows recent queries with success/failure status
 */

import { useState } from "react"
import { useQuery } from "../contexts/QueryContext"

const QueryHistory = () => {
  const { queryHistory, setQuery } = useQuery()
  const [isExpanded, setIsExpanded] = useState(false)

  const handleQueryClick = (query) => {
    setQuery(query)
  }

  const handleClearHistory = () => {
    // In a real app, you'd have a clearHistory action
    console.log("Clear history clicked")
  }

  const formatTimeAgo = (timestamp) => {
    const now = new Date()
    const past = new Date(timestamp)
    const diff = now - past

    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (minutes < 1) return "Just now"
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    return `${days}d ago`
  }

  if (!queryHistory || queryHistory.length === 0) {
    return (
      <div className="query-history empty">
        <h3>🕒 Recent Queries</h3>
        <div className="empty-history">
          <span className="empty-icon">📝</span>
          <p>No queries yet</p>
          <p>Your query history will appear here</p>
        </div>
      </div>
    )
  }

  const displayedHistory = isExpanded ? queryHistory : queryHistory.slice(0, 5)

  return (
    <div className="query-history">
      <div className="history-header">
        <h3>🕒 Recent Queries</h3>
        {queryHistory.length > 0 && (
          <button onClick={handleClearHistory} className="clear-history-button" title="Clear all history">
            🗑️
          </button>
        )}
      </div>

      <div className="history-list">
        {displayedHistory.map((item, index) => (
          <div
            key={index}
            className={`history-item ${item.success ? "success" : "error"}`}
            onClick={() => handleQueryClick(item.query)}
            title="Click to reuse this query"
          >
            <div className="history-content">
              <div className="history-status">
                {item.success ? (
                  <span className="status-icon success">✅</span>
                ) : (
                  <span className="status-icon error">❌</span>
                )}
              </div>

              <div className="history-text">
                <div className="history-query">
                  {item.query.length > 80 ? `${item.query.substring(0, 80)}...` : item.query}
                </div>
                {item.error && <div className="history-error">Error: {item.error}</div>}
              </div>

              <div className="history-time">{formatTimeAgo(item.timestamp)}</div>
            </div>
          </div>
        ))}
      </div>

      {queryHistory.length > 5 && (
        <button onClick={() => setIsExpanded(!isExpanded)} className="expand-history-button">
          {isExpanded ? <>Show Less ▲</> : <>Show More ({queryHistory.length - 5}) ▼</>}
        </button>
      )}
    </div>
  )
}

export default QueryHistory
