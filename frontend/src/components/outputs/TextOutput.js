"use client"

/**
 * Text Output Component
 * Displays AI-generated text responses with formatting
 */

import { useState } from "react"

const TextOutput = ({ data }) => {
  const [isCopied, setIsCopied] = useState(false)

  const textResponse = data?.textResponse || ""

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(textResponse)
      setIsCopied(true)
      setTimeout(() => setIsCopied(false), 2000)
    } catch (error) {
      console.error("Failed to copy text:", error)
    }
  }

  const formatText = (text) => {
    // Simple text formatting for better readability
    return text
      .split("\n")
      .map((paragraph, index) => {
        if (paragraph.trim() === "") return null

        // Check if paragraph contains bullet points
        if (paragraph.includes("•") || paragraph.includes("-")) {
          const items = paragraph.split(/[•-]/).filter((item) => item.trim())
          if (items.length > 1) {
            return (
              <ul key={index} className="text-list">
                {items.map((item, itemIndex) => (
                  <li key={itemIndex}>{item.trim()}</li>
                ))}
              </ul>
            )
          }
        }

        // Check if paragraph looks like a header (short and ends with :)
        if (paragraph.length < 100 && paragraph.endsWith(":")) {
          return (
            <h4 key={index} className="text-header">
              {paragraph}
            </h4>
          )
        }

        return (
          <p key={index} className="text-paragraph">
            {paragraph}
          </p>
        )
      })
      .filter(Boolean)
  }

  if (!textResponse) {
    return (
      <div className="text-output-empty">
        <p>No text response available.</p>
      </div>
    )
  }

  return (
    <div className="text-output">
      <div className="text-output-header">
        <h3>🤖 AI Analysis</h3>
        <button onClick={handleCopy} className={`copy-button ${isCopied ? "copied" : ""}`} title="Copy to clipboard">
          {isCopied ? "✅ Copied!" : "📋 Copy"}
        </button>
      </div>

      <div className="text-content">{formatText(textResponse)}</div>

      <div className="text-output-footer">
        <span className="word-count">
          📊 {textResponse.split(" ").length} words • {textResponse.length} characters
        </span>
      </div>
    </div>
  )
}

export default TextOutput
