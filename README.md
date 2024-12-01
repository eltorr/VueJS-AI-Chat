# AI Chat Application

A real-time chat application built with Vue.js and FastAPI, featuring AI-powered responses using OpenAI's API.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js (v16 or higher)
- npm or yarn
- OpenAI API key

### Backend Setup
1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file with your OpenAI API key:
```plaintext
OPENAI_API_KEY=your_api_key_here
```

4. Start the FastAPI server:
```bash
uvicorn app:app --host 0.0.0.0 --port 5001 --reload
```

### Frontend Setup
1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run serve
```

## 📁 Project Structure
```
.
├── frontend/          # Vue.js application
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── assets/
└── backend/          # FastAPI server
    ├── app.py
    └── requirements.txt
```

## 🔑 Environment Variables

### Backend Variables
- `OPENAI_API_KEY`: Your OpenAI API key

## 🌐 API Documentation
Once the backend server is running:
- API endpoint: `http://localhost:5001`
- Interactive API documentation: `http://localhost:5001/docs`

## ✨ Features
- Real-time chat interface
- AI-powered responses using OpenAI
- Dark/Light mode toggle
- Markdown support with syntax highlighting
- Code block copying functionality

## 🛠️ Technologies Used
- Frontend:
  - Vue.js 3
  - Axios
  - Marked (for Markdown rendering)
  - Highlight.js
- Backend:
  - FastAPI
  - OpenAI API
  - Python-dotenv

## 📄 License
This project is licensed under the MIT License.
