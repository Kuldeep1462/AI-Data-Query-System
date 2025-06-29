const Header = () => {
  return (
    <header className="app-header">
      <div className="header-container">
        <div className="header-brand">
          <div className="brand-logo">
            <span className="logo-icon">🤖</span>
            <span className="logo-text">AI Query System</span>
          </div>
          <div className="brand-tagline">Natural Language Data Analytics</div>
        </div>

        <nav className="header-nav">
          <div className="nav-links">
            <a href="#home" className="nav-link active">
              <span className="nav-icon">🏠</span>
              Home
            </a>
          </div>
        </nav>

        <div className="header-actions">
          <div className="system-status">
            <span className="status-indicator online"></span>
            <span className="status-text">System Online</span>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
