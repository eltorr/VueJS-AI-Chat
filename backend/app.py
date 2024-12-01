from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

class ChatMessage(BaseModel):
    messages: List[Dict[str, str]]

@app.post("/api/chat")
async def chat(message: ChatMessage):
    print("Endpoint hit!")  # Debug print
    try:
        print("Received data:", message.dict())  # Debug print
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=message.messages
        )
        
        return {
            'message': response.choices[0].message.content,
            'status': 'success'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# For development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)