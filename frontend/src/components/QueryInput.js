"use client"

/**
 * Query Input Component
 * Handles user input for natural language queries
 */

import { useState, useRef, useEffect } from "react"

const QueryInput = ({ onSubmit, isLoading, currentQuery, onQueryChange }) => {
  const [localQuery, setLocalQuery] = useState(currentQuery || "")
  const textareaRef = useRef(null)

  useEffect(() => {
    setLocalQuery(currentQuery || "")
  }, [currentQuery])

  const handleInputChange = (e) => {
    const value = e.target.value
    setLocalQuery(value)
    onQueryChange(value)

    // Auto-resize textarea
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = "auto"
      textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!isLoading && localQuery.trim()) {
      onSubmit(localQuery.trim())
    }
  }

  const handleKeyDown = (e) => {
    // Submit on Ctrl+Enter or Cmd+Enter
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const handleClear = () => {
    setLocalQuery("")
    onQueryChange("")
    textareaRef.current?.focus()
  }

  return (
    <div className="query-input-container">
      <form onSubmit={handleSubmit} className="query-form">
        <div className="input-wrapper">
          <textarea
            ref={textareaRef}
            value={localQuery}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="Ask me anything about your wealth management data...

Examples:
• What are the top five portfolios of our wealth members?
• Breakup of portfolio values by relationship manager
• Which clients hold the most equity investments?"
            className="query-textarea"
            disabled={isLoading}
            rows={3}
            maxLength={500}
          />

          {localQuery && (
            <button
              type="button"
              onClick={handleClear}
              className="clear-input-button"
              disabled={isLoading}
              title="Clear input"
            >
              ✕
            </button>
          )}
        </div>

        <div className="input-actions">
          <div className="input-info">
            <span className="character-count">{localQuery.length}/500</span>
            <span className="keyboard-hint">Ctrl+Enter to submit</span>
          </div>

          <button
            type="submit"
            className={`submit-button ${isLoading ? "loading" : ""}`}
            disabled={isLoading || !localQuery.trim()}
          >
            {isLoading ? (
              <>
                <span className="spinner"></span>
                Processing...
              </>
            ) : (
              <>
                <span className="submit-icon">🚀</span>
                Ask AI
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}

export default QueryInput
