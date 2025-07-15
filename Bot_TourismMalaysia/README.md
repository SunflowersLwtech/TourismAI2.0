# 🇲🇾 Malaysia Tourism AI Chatbot

A sophisticated AI-powered tourism assistant specializing in Malaysia travel recommendations, powered by fine-tuned Google Gemini AI and deployed on cloud infrastructure.

## 🌟 Project Overview

The Malaysia Tourism AI Chatbot is an intelligent conversational system designed to provide comprehensive travel guidance for Malaysia. Built with modern web technologies and powered by a fine-tuned Gemini AI model, it offers personalized recommendations for attractions, accommodations, dining, and cultural experiences across all Malaysian states.

## ✨ Key Features

- 🧠 **Fine-tuned Gemini AI** - Specialized knowledge about Malaysia tourism with custom training data
- 🌍 **Comprehensive Coverage** - Information about all 13 Malaysian states and federal territories
- 📱 **Responsive Interface** - Modern Streamlit-based web application optimized for all devices
- ⚡ **Real-time Responses** - Instant AI-powered recommendations with streaming capabilities
- 🚀 **Cloud Deployment** - Globally accessible via Render cloud platform
- 🔧 **Configurable Parameters** - Adjustable temperature and token limits for response customization
- 📊 **Health Monitoring** - Built-in system status and performance tracking
- 🎯 **Multi-turn Conversations** - Context-aware dialogue for natural interactions

## 🏗️ System Architecture

```
┌─────────────────┐    HTTP/REST API    ┌──────────────────┐    Vertex AI    ┌─────────────────┐
│  Streamlit      │ ◄─────────────────► │  FastAPI         │ ◄─────────────► │  Fine-tuned     │
│  Frontend       │                     │  Backend         │                 │  Gemini Model   │
│  (Port 8501)    │                     │  (Port 8000)     │                 │  (Endpoint)     │
└─────────────────┘                     └──────────────────┘                 └─────────────────┘
```

### Component Details

**Frontend Layer:**
- Streamlit web application with custom CSS styling
- Real-time chat interface with conversation history
- Parameter controls for AI model configuration
- Health status monitoring and debug information

**Backend Layer:**
- FastAPI REST API with CORS support
- Google Gen AI SDK integration
- Streaming response capabilities
- Comprehensive error handling and logging

**AI Layer:**
- Fine-tuned Gemini model on Google Vertex AI
- Custom training data focused on Malaysia tourism
- Endpoint: `projects/bright-coyote-463315-q8/locations/us-west1/endpoints/6528596580524621824`

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Google Cloud Project with Vertex AI enabled
- Gemini API key
- Git

### Local Development

1. **Clone the Repository**
   ```bash
   git clone https://github.com/SunflowersLwtech/malaysia-ai-backend.git
   cd malaysia-ai-backend
   ```

2. **Set Up Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r streamlit_requirements.txt
   ```

3. **Configure Environment Variables**
   Create a `.env` file:
   ```env
   GOOGLE_CLOUD_PROJECT=bright-coyote-463315-q8
   GOOGLE_CLOUD_LOCATION=us-west1
   VERTEX_AI_ENDPOINT=projects/bright-coyote-463315-q8/locations/us-west1/endpoints/6528596580524621824
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Start Backend Server**
   ```bash
   uvicorn api_server_genai:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Start Frontend Application**
   ```bash
   # In a new terminal
   streamlit run streamlit_app.py --server.port 8501
   ```

6. **Access the Application**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🌐 Cloud Deployment

### Render Deployment

The application is configured for seamless deployment on Render cloud platform:

**Backend Service:**
- Environment: Docker
- Build: Automated via Dockerfile
- Health Check: `/health` endpoint
- Auto-deploy: Enabled

**Frontend Service:**
- Environment: Docker/Python
- Streamlit configuration optimized for cloud
- Environment variables for backend connection

### Deployment URLs
- **Production Backend**: https://malaysia-ai-backend.onrender.com
- **Production Frontend**: https://malaysia-ai-frontend.onrender.com

## 📚 API Documentation

### Core Endpoints

#### Health Check
```http
GET /health
```
Returns system status and configuration information.

#### Chat Endpoint
```http
POST /chat
Content-Type: application/json

{
  "message": "What are the best places to visit in Kuala Lumpur?",
  "temperature": 0.7,
  "max_tokens": 8192
}
```

#### Streaming Chat
```http
POST /chat-stream
Content-Type: application/json
```
Returns server-sent events for real-time streaming responses.

### Response Format
```json
{
  "response": "AI-generated response text",
  "model_used": "vertex-ai-endpoint"
}
```

## 🛠️ Technology Stack

### Backend Technologies
- **FastAPI** - Modern Python web framework
- **Google Gen AI SDK** - Official Google AI integration
- **Uvicorn** - ASGI server for production deployment
- **Pydantic** - Data validation and serialization
- **Google Cloud Vertex AI** - AI model hosting and inference

### Frontend Technologies
- **Streamlit** - Rapid web app development framework
- **Requests** - HTTP client for API communication
- **Custom CSS** - Enhanced UI styling and responsiveness

### Infrastructure
- **Docker** - Containerization for consistent deployment
- **Render** - Cloud platform for hosting and scaling
- **GitHub Actions** - CI/CD pipeline (optional)

## 📊 Performance Characteristics

### Response Times
- **Local Development**: 1-3 seconds average response time
- **Cloud Deployment**: 2-5 seconds (including cold start)
- **Streaming Mode**: Real-time token delivery

### Scalability
- **Concurrent Users**: Supports multiple simultaneous conversations
- **Rate Limiting**: Configurable via Vertex AI quotas
- **Auto-scaling**: Handled by Render platform

## 🔧 Configuration Options

### AI Model Parameters
- **Temperature**: 0.0-2.0 (creativity control)
- **Max Tokens**: 1000-16384 (response length)
- **Top-p**: 0.95 (nucleus sampling)
- **Safety Settings**: Configurable content filtering

### Application Settings
- **CORS**: Configurable for cross-origin requests
- **Logging**: Structured logging with multiple levels
- **Health Checks**: Automated monitoring endpoints

## 🧪 Testing

### Manual Testing
1. Access the frontend application
2. Verify backend connectivity in sidebar
3. Send test messages about Malaysia tourism
4. Validate AI responses for accuracy and relevance

### API Testing
```bash
# Test health endpoint
curl https://malaysia-ai-backend.onrender.com/health

# Test chat endpoint
curl -X POST https://malaysia-ai-backend.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about Penang food"}'
```

## 🔒 Security Considerations

### API Security
- CORS configuration for controlled access
- Environment variable protection for sensitive data
- Input validation and sanitization
- Rate limiting via cloud provider

### Data Privacy
- No persistent storage of user conversations
- Temporary processing of chat messages
- Compliance with Google Cloud security standards

## 📈 Monitoring and Maintenance

### Health Monitoring
- Built-in health check endpoints
- Real-time status indicators in frontend
- Automated deployment health verification

### Logging
- Structured application logging
- Error tracking and debugging information
- Performance metrics collection

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit pull request with detailed description

### Code Standards
- Python PEP 8 compliance
- Type hints for better code documentation
- Comprehensive error handling
- Clear function and variable naming

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Cloud Vertex AI** - AI model hosting and inference
- **Streamlit Community** - Frontend framework and components
- **FastAPI Team** - Backend framework development
- **Malaysia Tourism Board** - Inspiration and domain knowledge

## 📞 Support

For questions, issues, or contributions:

- **GitHub Issues**: [Project Issues](https://github.com/SunflowersLwtech/malaysia-ai-backend/issues)
- **Documentation**: [Deployment Guide](RENDER_DEPLOYMENT.md)
- **API Docs**: [Interactive API Documentation](https://malaysia-ai-backend.onrender.com/docs)

---

**Built with ❤️ for Malaysia Tourism | Powered by Google AI**