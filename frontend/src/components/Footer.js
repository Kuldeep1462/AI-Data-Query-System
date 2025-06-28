const Footer = () => {
  return (
    <footer className="app-footer">
      <div className="footer-container">
        <div className="footer-section">
          <h4>🤖 AI Query System</h4>
          <p>Powered by Gemini AI & FastAPI</p>
        </div>

        <div className="footer-section">
          <h4>📊 Data Sources</h4>
          <ul>
            <li>MongoDB - Client Profiles</li>
            <li>MySQL - Investment Data</li>
          </ul>
        </div>

        <div className="footer-section">
          <h4>🔧 Tech Stack</h4>
          <ul>
            <li>React.js Frontend</li>
            <li>Python FastAPI Backend</li>
            <li>LangChain Architecture</li>
          </ul>
        </div>

        <div className="footer-section">
          <div className="footer-info">
            <p>© 2024 Wealth Management AI System</p>
            <p>Built for Film Stars & Sports Personalities Portfolio Management</p>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer
