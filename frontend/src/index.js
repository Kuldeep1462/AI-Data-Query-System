/**
 * Application Entry Point
 * AI Data Query System
 */

import React from "react"
import ReactDOM from "react-dom/client"
import "./App.css"
import App from "./App"

// Create root element
const root = ReactDOM.createRoot(document.getElementById("root"))

// Render the application
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)

// Performance monitoring (optional)
if (process.env.NODE_ENV === "development") {
  console.log("🚀 AI Data Query System started in development mode")
}
