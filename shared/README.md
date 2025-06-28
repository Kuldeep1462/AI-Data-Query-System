# 🤖 AI Data Query System

**Natural Language Cross-Platform Data Query RAG Agent**

A sophisticated AI-powered system that allows business users to query multiple data sources using plain English and receive intelligent responses in various formats (text, tables, charts).

## 🎯 Project Overview

This system is designed for wealth management companies managing ₹100+ crore portfolios for film stars and sports personalities. It integrates with MongoDB (client profiles) and MySQL (investment transactions) to provide instant insights through natural language queries.

### Key Features

- 🗣️ **Natural Language Processing**: Ask questions in plain English
- 📊 **Multi-format Responses**: Get answers as text summaries, tables, or charts
- 🔄 **Real-time Data**: Live connection to MongoDB and MySQL databases
- 🤖 **AI-Powered**: Uses Google Gemini AI for intelligent query understanding
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices
- 🚀 **Production Ready**: Built with enterprise-grade architecture

## 🏗️ Architecture

\`\`\`
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React.js      │    │   FastAPI       │    │   Databases     │
│   Frontend      │◄──►│   Backend       │◄──►│   MongoDB       │
│                 │    │                 │    │   MySQL         │
│   - Query Input │    │   - Gemini AI   │    │   - Client Data │
│   - Results UI  │    │   - LangChain   │    │   - Transactions│
│   - Charts      │    │   - Data Proc.  │    │   - Analytics   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
\`\`\`

## 🛠️ Tech Stack

### Frontend
- **React.js 18** - Modern UI framework
- **Chart.js** - Data visualization
- **Axios** - HTTP client
- **CSS3** - Custom styling (no external UI library)

### Backend
- **Python 3.11+** - Core language
- **FastAPI** - High-performance web framework
- **Google Gemini AI** - Natural language processing
- **LangChain** - AI application framework
- **Motor** - Async MongoDB driver
- **aiomysql** - Async MySQL driver

### Databases
- **MongoDB** - Client profiles and metadata
- **MySQL** - Investment transactions and portfolio data

### AI & Analytics
- **Google Gemini Pro** - Language model
- **Matplotlib/Seaborn** - Chart generation
- **Pandas** - Data processing

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+** and npm
- **Python 3.11+** and pip
- **MongoDB** access (cloud or local)
- **MySQL** server (local or remote)
- **Google Gemini API Key**

### 1. Clone and Setup

\`\`\`bash
# Clone the repository
git clone <repository-url>
cd ai-data-query-system

# Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup frontend
cd ../frontend
npm install
\`\`\`

### 2. Environment Configuration

Create `backend/.env`:

\`\`\`env
# Database Configuration
MONGODB_URL="mongodb+srv://valuefy:kuldeep01@cluster0.hd0i76u.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
MYSQL_HOST="localhost"
MYSQL_USER="root"
MYSQL_PASSWORD="root"
MYSQL_DATABASE="wealth_portfolio"

# AI Configuration
GEMINI_API_KEY="AIzaSyA6YbOvbnnDMzzzjDdBwkYz36gJZz39eMw"

# Application Configuration
APP_NAME="AI Data Query System"
DEBUG=true
LOG_LEVEL="INFO"
\`\`\`

### 3. Database Setup

**MongoDB**: The system will automatically create sample data on first run.

**MySQL**: Create the database and table:

\`\`\`sql
CREATE DATABASE wealth_portfolio;
USE wealth_portfolio;

CREATE TABLE investments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id VARCHAR(10) NOT NULL,
    portfolio_value BIGINT NOT NULL,
    relationship_manager VARCHAR(100) NOT NULL,
    investment_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
\`\`\`

### 4. Run the Application

**Start Backend** (Terminal 1):
\`\`\`bash
cd backend
python main.py
# Server runs on http://localhost:8000
\`\`\`

**Start Frontend** (Terminal 2):
\`\`\`bash
cd frontend
npm start
# App opens at http://localhost:3000
\`\`\`

## 📖 Usage Guide

### Example Queries

Try these natural language queries:

**Portfolio Analysis:**
- "What are the top five portfolios of our wealth members?"
- "Show me the portfolio breakdown by investment type"
- "Which clients have the highest portfolio values?"

**Relationship Manager Insights:**
- "Breakup of portfolio values by relationship manager"
- "Who are the top relationship managers?"
- "Show me performance by relationship manager"

**Client Information:**
- "List all clients with conservative risk appetite"
- "Which clients hold the most equity investments?"
- "Show me clients from Mumbai"

### Response Formats

The system provides three types of responses:

1. **📄 Text Summary**: AI-generated insights and explanations
2. **📊 Table View**: Structured data in sortable, filterable tables
3. **📈 Chart View**: Visual representations (bar, pie, line charts)

## 🔧 Development

### Project Structure

\`\`\`
ai-data-query-system/
├── backend/                 # Python FastAPI backend
│   ├── main.py             # Application entry point
│   ├── routes/             # API route handlers
│   ├── services/           # Business logic
│   ├── db/                 # Database connections
│   ├── utils/              # Utility functions
│   └── requirements.txt    # Python dependencies
├── frontend/               # React.js frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API communication
│   │   ├── contexts/       # State management
│   │   └── App.js          # Main application
│   ├── public/             # Static assets
│   └── package.json        # Node.js dependencies
└── shared/                 # Documentation and assets
    └── README.md           # This file
\`\`\`

### Key Components

**Backend Services:**
- `QueryProcessor`: Handles AI query processing with Gemini
- `MongoDB`: Client profile data management
- `MySQL`: Investment transaction handling
- `GraphGenerator`: Chart and visualization creation

**Frontend Components:**
- `QueryInput`: Natural language input interface
- `OutputTabs`: Multi-format result display
- `ExampleQueries`: Predefined query suggestions
- `QueryHistory`: Recent query tracking

### API Endpoints

- `POST /api/v1/query` - Process natural language query
- `GET /api/v1/query/examples` - Get example queries
- `GET /api/v1/query/stats` - Get system statistics
- `GET /health` - Health check endpoint

## 🧪 Testing

### Backend Testing
\`\`\`bash
cd backend
pytest tests/ -v
\`\`\`

### Frontend Testing
\`\`\`bash
cd frontend
npm test
\`\`\`

### Manual Testing
1. Start both backend and frontend
2. Try example queries from different categories
3. Test all three output formats (text, table, chart)
4. Verify responsive design on different screen sizes

## 🚀 Deployment

### Backend Deployment (FastAPI)

**Using Docker:**
\`\`\`dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
\`\`\`

**Using Vercel/Railway/Render:**
- Set environment variables
- Deploy from GitHub repository
- Configure build command: `pip install -r requirements.txt`
- Configure start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend Deployment (React)

**Using Vercel/Netlify:**
\`\`\`bash
npm run build
# Deploy the 'build' folder
\`\`\`

**Environment Variables:**
\`\`\`env
REACT_APP_API_URL=https://your-backend-url.com
\`\`\`

## 🔒 Security Considerations

- **API Keys**: Store securely in environment variables
- **Database Access**: Use connection strings with proper authentication
- **CORS**: Configure allowed origins for production
- **Input Validation**: All user inputs are validated and sanitized
- **Rate Limiting**: Implement rate limiting for production use

## 📊 Performance Optimization

- **Database Indexing**: Proper indexes on frequently queried fields
- **Caching**: Redis caching for frequent queries (future enhancement)
- **Connection Pooling**: Async database connection pools
- **Code Splitting**: React lazy loading for better performance
- **CDN**: Static asset delivery via CDN

## 🔮 Future Enhancements

### Phase 2 Features
- **Authentication**: JWT-based user authentication
- **Role-based Access**: Different access levels for users
- **Query Caching**: Redis-based response caching
- **Advanced Analytics**: Time-series analysis and predictions

### Phase 3 Features
- **Multi-LLM Support**: OpenAI, Anthropic, and other providers
- **Vector Database**: RAG with embeddings for better context
- **Real-time Updates**: WebSocket connections for live data
- **Mobile App**: React Native mobile application

### Phase 4 Features
- **Voice Queries**: Speech-to-text integration
- **Advanced Visualizations**: D3.js custom charts
- **Export Features**: PDF reports and Excel exports
- **Audit Logging**: Complete query and response logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint for JavaScript code
- Write comprehensive tests
- Update documentation for new features
- Use semantic commit messages

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

1. **Documentation**: Check this README and inline code comments
2. **Issues**: Create GitHub issues for bugs and feature requests
3. **Discussions**: Use GitHub Discussions for general questions

## 🙏 Acknowledgments

- **Google Gemini AI** for natural language processing
- **FastAPI** for the excellent Python web framework
- **React.js** for the powerful frontend framework
- **Chart.js** for beautiful data visualizations
- **MongoDB** and **MySQL** for reliable data storage

---

**Built with ❤️ for Wealth Management Excellence**

*This system represents the future of data analytics - where natural language meets artificial intelligence to deliver instant insights.*
