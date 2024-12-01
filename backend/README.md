

# AI Web Chat Backend

This is a FastAPI-based backend service for the AI Web Chat application.

## Setup

1. Install required dependencies:

```bash
pip install fastapi uvicorn python-dotenv openai
```

2. Create a `.env` file in the backend directory and add your OpenAI API key:

```plaintext
OPENAI_API_KEY=your_api_key_here
```

## Running the Application

You can run the application in two ways:

### Using Python directly:

```bash
python app.py
```

### Using Uvicorn (recommended for development):

```bash
uvicorn app:app --host 0.0.0.0 --port 5001 --reload
```

The `--reload` flag enables auto-reload when you make changes to the code.

## API Documentation

Once the server is running:
- The API will be available at: `http://localhost:5001`
- Interactive API documentation can be found at: `http://localhost:5001/docs`

