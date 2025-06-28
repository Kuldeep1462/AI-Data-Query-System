"use client"
import { useQuery } from "../contexts/QueryContext"

// Import sub-components
import TextOutput from "./outputs/TextOutput"
import TableOutput from "./outputs/TableOutput"
import ChartOutput from "./outputs/ChartOutput"

const OutputTabs = ({ results }) => {
  const { activeTab, setActiveTab } = useQuery()

  const tabs = [
    {
      id: "text",
      label: "📄 Text Summary",
      icon: "📄",
      component: TextOutput,
      hasData: Boolean(results?.textResponse),
    },
    {
      id: "table",
      label: "📊 Table View",
      icon: "📊",
      component: TableOutput,
      hasData: Boolean(results?.tableData?.rows?.length > 0),
    },
    {
      id: "chart",
      label: "📈 Chart View",
      icon: "📈",
      component: ChartOutput,
      hasData: Boolean(results?.chartData?.datasets?.length > 0),
    },
  ]

  const handleTabClick = (tabId) => {
    setActiveTab(tabId)
  }

  const activeTabData = tabs.find((tab) => tab.id === activeTab)

  return (
    <div className="output-tabs">
      {/* Tab Navigation */}
      <div className="tab-navigation">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => handleTabClick(tab.id)}
            className={`tab-button ${activeTab === tab.id ? "active" : ""} ${!tab.hasData ? "disabled" : ""}`}
            disabled={!tab.hasData}
            title={!tab.hasData ? "No data available for this view" : `Switch to ${tab.label}`}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
            {!tab.hasData && <span className="no-data-indicator">•</span>}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTabData && (
          <div className={`tab-panel tab-panel-${activeTab}`}>
            {activeTabData.hasData ? (
              <activeTabData.component data={results} />
            ) : (
              <div className="no-data-message">
                <div className="no-data-icon">📭</div>
                <h3>No Data Available</h3>
                <p>This view doesn't have data for the current query result.</p>
                <p>Try switching to a different tab or submit a new query.</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Results Metadata */}
      {results?.timestamp && (
        <div className="results-metadata">
          <span className="timestamp">🕒 Generated: {new Date(results.timestamp).toLocaleString()}</span>
        </div>
      )}
    </div>
  )
}

export default OutputTabs
