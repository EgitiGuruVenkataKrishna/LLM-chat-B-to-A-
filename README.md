# LLM Chat API 🤖

A production-ready FastAPI backend that integrates with OpenAI's API to provide AI-powered chat capabilities with multiple personas.

**Part of my 39-Day AI Systems Engineer Challenge** - [Follow my journey on LinkedIn]: https://www.linkedin.com/in/guru-venkata-krishna-egiti/

---

## 🎯 Features

- ✅ RESTful API with automatic documentation
- ✅ OpenAI GPT-3.5/4 integration
- ✅ Multiple AI personas (Coder, Teacher, Professional)
- ✅ Environment-based configuration
- ✅ Comprehensive logging
- ✅ Error handling and validation
- ✅ Token usage tracking

---

## 🛠️ Tech Stack

- **Backend Framework:** FastAPI
- **AI Integration:** Groq API
- **Language:** Python 3.9+
- **Environment Management:** python-dotenv

---

## 📋 Prerequisites

- Python 3.9 or higher
- Groq Api Key (Take from:console.groq.com/keys)
- pip (Python package manager)

---

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/EgitiGuruVenkataKrishna/llm-chat-api.git
cd llm-chat-api
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv
venv\Scripts\activate #On mac:source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root:
```
OPENAI_API_KEY=your-api-key-here
```

### 5. Run the Application
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

---

## 📚 API Endpoints

### Health Check
```http
GET /
```
Returns API status.

**Response:**
```json
{
  "status": "healthy",
  "message": "LLM Chat API is running"
}
```

### Chat (General)
```http
POST /chat
```

**Request Body:**
```json
{
  "message": "What is machine learning?",
  "temperature": 0.7,
  "max_tokens": 500
}
```

**Response:**
```json
{
  "response": "Machine learning is...",
  "tokens_used": 150
}
```

### Chat with Coder Persona
```http
POST /chat/coder
```
Optimized for coding questions and technical explanations.

### Chat with Teacher Persona
```http
POST /chat/teacher
```
Explains concepts in simple, educational terms.

---

## 📖 Interactive Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

You can test all endpoints directly from the browser!

---

## 🧪 Testing

### Using cURL
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

### Using Python
```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={"message": "Explain FastAPI"}
)
print(response.json())
```

---

## 🔒 Security Notes

- Never commit `.env` file to Git
- API keys are loaded from environment variables
- Rate limiting recommended for production
- Input validation handled by Pydantic models

---

## 📈 Future Improvements

- [ ] Add authentication (API keys)
- [ ] Implement rate limiting
- [ ] Add response caching
- [ ] Support for streaming responses
- [ ] Database integration for conversation history
- [ ] Docker containerization
- [ ] Unit tests

---

## 🐛 Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### "Invalid API key" error
- Check your `.env` file has the correct OpenAI API key
- Ensure `.env` is in the same directory as `main.py`

### Port already in use
```bash
uvicorn main:app --reload --port 8001
```

---

## 📝 Logs

Application logs are stored in `api.log`. View them in real-time:
```bash
tail -f api.log
```

---

## 🤝 Contributing

This is a learning project, but feedback and suggestions are welcome! Feel free to:
- Open an issue
- Submit a pull request
- Share your experience

---

## 👨‍💻 Author

**Guru Venkata Krishna**
- LinkedIn: https://www.linkedin.com/in/guru-venkata-krishna-egiti/
- GitHub: [@EgitiGuruVenkataKrishna](https://github.com/EgitiGuruVenakataKrishna)
- Email: yegitigvkrishna@gmail.com

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🙏 Acknowledgments

- Part of my [39-Day AI Systems Engineer Challenge](https://www.linkedin.com/posts/guru-venkata-krishna-egiti_39daychallenge-aiengineering-activity-7428589216592195584-U1j4)
- Built following FastAPI and OpenAI best practices
- Inspired by real-world production AI systems

---

**⭐ If this helped you, please star the repo!**