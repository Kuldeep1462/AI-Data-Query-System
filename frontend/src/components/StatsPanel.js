const StatsPanel = ({ stats }) => {
  if (!stats) {
    return null
  }

  const statItems = [
    {
      key: "total_clients",
      label: "Total Clients",
      value: stats.total_clients,
      icon: "👥",
    },
    {
      key: "total_portfolio_value",
      label: "Portfolio Value",
      value: stats.total_portfolio_value,
      icon: "💰",
    },
    {
      key: "relationship_managers",
      label: "Relationship Managers",
      value: stats.relationship_managers,
      icon: "🤝",
    },
    {
      key: "active_portfolios",
      label: "Active Portfolios",
      value: stats.active_portfolios,
      icon: "📊",
    },
  ]

  return (
    <div className="stats-panel">
      <div className="stats-grid">
        {statItems.map(({ key, label, value, icon }) => (
          <div key={key} className="stat-item">
            <div className="stat-icon">{icon}</div>
            <div className="stat-content">
              <div className="stat-value">{value}</div>
              <div className="stat-label">{label}</div>
            </div>
          </div>
        ))}
      </div>

      {stats.last_updated && (
        <div className="stats-footer">
          <span className="last-updated">🕐 Last updated: {new Date(stats.last_updated).toLocaleString()}</span>
        </div>
      )}
    </div>
  )
}

export default StatsPanel
