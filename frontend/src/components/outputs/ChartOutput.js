"use client"

/**
 * Chart Output Component
 * Displays data visualizations using Chart.js
 */

import { useRef, useEffect, useState } from "react"
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js"
import { Bar, Pie, Line } from "react-chartjs-2"

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, LineElement, PointElement, Title, Tooltip, Legend)

const ChartOutput = ({ data }) => {
  const chartRef = useRef(null)
  const [chartType, setChartType] = useState("bar")

  const chartData = data?.chartData || {}
  const { type, title, labels, datasets } = chartData

  // Set initial chart type from data
  useEffect(() => {
    if (type) {
      setChartType(type)
    }
  }, [type])

  // Chart configuration options
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top",
        labels: {
          padding: 20,
          usePointStyle: true,
        },
      },
      title: {
        display: !!title,
        text: title,
        font: {
          size: 16,
          weight: "bold",
        },
        padding: 20,
      },
      tooltip: {
        backgroundColor: "rgba(0, 0, 0, 0.8)",
        titleColor: "white",
        bodyColor: "white",
        borderColor: "rgba(255, 255, 255, 0.2)",
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          label: (context) => {
            const value = context.parsed.y || context.parsed
            if (typeof value === "number" && value > 1000) {
              return `${context.dataset.label}: ₹${value.toLocaleString()}`
            }
            return `${context.dataset.label}: ${value}`
          },
        },
      },
    },
    scales:
      chartType !== "pie"
        ? {
            x: {
              grid: {
                display: false,
              },
              ticks: {
                maxRotation: 45,
                minRotation: 0,
              },
            },
            y: {
              beginAtZero: true,
              grid: {
                color: "rgba(0, 0, 0, 0.1)",
              },
              ticks: {
                callback: (value) => {
                  if (value >= 1000000) {
                    return "₹" + (value / 1000000).toFixed(1) + "M"
                  } else if (value >= 1000) {
                    return "₹" + (value / 1000).toFixed(1) + "K"
                  }
                  return "₹" + value
                },
              },
            },
          }
        : undefined,
  }

  // Format chart data
  const formattedChartData = {
    labels: labels || [],
    datasets: datasets || [],
  }

  const handleChartTypeChange = (newType) => {
    setChartType(newType)
  }

  const handleDownload = () => {
    if (chartRef.current) {
      const chart = chartRef.current
      const url = chart.canvas.toDataURL("image/png")
      const link = document.createElement("a")
      link.download = `chart-${new Date().toISOString().split("T")[0]}.png`
      link.href = url
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  if (!labels?.length || !datasets?.length) {
    return (
      <div className="chart-output-empty">
        <div className="empty-state">
          <span className="empty-icon">📈</span>
          <h3>No Chart Data</h3>
          <p>No visualization data available for this query.</p>
          <p>Try a query that involves numerical comparisons or breakdowns.</p>
        </div>
      </div>
    )
  }

  const renderChart = () => {
    const commonProps = {
      ref: chartRef,
      data: formattedChartData,
      options: chartOptions,
    }

    switch (chartType) {
      case "pie":
        return <Pie {...commonProps} />
      case "line":
        return <Line {...commonProps} />
      case "bar":
      default:
        return <Bar {...commonProps} />
    }
  }

  return (
    <div className="chart-output">
      {/* Chart Controls */}
      <div className="chart-controls">
        <div className="chart-type-selector">
          <span className="selector-label">Chart Type:</span>
          <div className="chart-type-buttons">
            {[
              { type: "bar", icon: "📊", label: "Bar" },
              { type: "pie", icon: "🥧", label: "Pie" },
              { type: "line", icon: "📈", label: "Line" },
            ].map(({ type: btnType, icon, label }) => (
              <button
                key={btnType}
                onClick={() => handleChartTypeChange(btnType)}
                className={`chart-type-button ${chartType === btnType ? "active" : ""}`}
                title={`Switch to ${label} chart`}
              >
                <span className="button-icon">{icon}</span>
                <span className="button-label">{label}</span>
              </button>
            ))}
          </div>
        </div>

        <button onClick={handleDownload} className="download-button" title="Download chart as PNG">
          📥 Download
        </button>
      </div>

      {/* Chart Container */}
      <div className="chart-container">
        <div className="chart-wrapper">{renderChart()}</div>
      </div>

      {/* Chart Information */}
      <div className="chart-info">
        <div className="chart-stats">
          <span className="stat-item">📊 Data Points: {labels.length}</span>
          <span className="stat-item">📈 Series: {datasets.length}</span>
        </div>
      </div>
    </div>
  )
}

export default ChartOutput
