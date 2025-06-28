"use client"

/**
 * Example Queries Component
 * Shows predefined example queries that users can click to try
 */

import { useState } from "react"

const ExampleQueries = ({ examples, onExampleClick, isLoading }) => {
  const [expandedCategory, setExpandedCategory] = useState(null)

  const toggleCategory = (categoryIndex) => {
    setExpandedCategory(expandedCategory === categoryIndex ? null : categoryIndex)
  }

  const handleExampleClick = (query) => {
    if (!isLoading) {
      onExampleClick(query)
    }
  }

  if (!examples || examples.length === 0) {
    return (
      <div className="example-queries loading">
        <h3>💡 Example Queries</h3>
        <div className="loading-placeholder">
          <div className="placeholder-line"></div>
          <div className="placeholder-line short"></div>
          <div className="placeholder-line"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="example-queries">
      <h3>💡 Example Queries</h3>
      <p className="examples-description">Click on any example below to try it out:</p>

      <div className="examples-list">
        {examples.map((category, categoryIndex) => (
          <div key={categoryIndex} className="example-category">
            <button
              className={`category-header ${expandedCategory === categoryIndex ? "expanded" : ""}`}
              onClick={() => toggleCategory(categoryIndex)}
              disabled={isLoading}
            >
              <span className="category-title">{category.category}</span>
              <span className="category-icon">{expandedCategory === categoryIndex ? "▼" : "▶"}</span>
            </button>

            {expandedCategory === categoryIndex && (
              <div className="category-queries">
                {category.queries.map((query, queryIndex) => (
                  <button
                    key={queryIndex}
                    className={`example-query-button ${isLoading ? "disabled" : ""}`}
                    onClick={() => handleExampleClick(query)}
                    disabled={isLoading}
                    title={isLoading ? "Please wait for current query to complete" : `Try: ${query}`}
                  >
                    <span className="query-icon">🔍</span>
                    <span className="query-text">{query}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="examples-footer">
        <p className="examples-tip">
          💡 <strong>Tip:</strong> You can ask questions in your own words too!
        </p>
      </div>
    </div>
  )
}

export default ExampleQueries
