from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
from openai import OpenAI
import os
from dotenv import load_dotenv
import ollama
import requests

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

# Configure OpenAI with new client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class Message(BaseModel):
    role: str
    content: str
    model: Optional[str] = None
    images: Optional[List[str]] = None

class OllamaMessage(BaseModel):
    messages: List[Message]
    model: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: str

@app.post("/api/chat")
async def chat(request: ChatRequest):
    print("OpenAI Endpoint hit!")
    try:
        print("Received request data:", request.dict())
        
        if request.model == "dall-e-3":
            # Handle DALL-E image generation
            response = client.images.generate(
                model="dall-e-3",
                prompt=request.messages[-1].content,  # Use the last message as the prompt
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            return {
                'message': f"![Generated Image]({response.data[0].url})",
                'status': 'success'
            }
            
        # Handle chat models
        if request.model != "gpt-4o-mini":
            raise HTTPException(
                status_code=400, 
                detail="For chat, currently only supporting gpt-4o-mini model"
            )
        
        formatted_messages = [
            {
                "role": msg.role,
                "content": msg.content
            } for msg in request.messages
        ]
        
        response = client.chat.completions.create(
            model=request.model,
            messages=formatted_messages
        )
        
        return {
            'message': response.choices[0].message.content,
            'status': 'success'
        }
    except Exception as e:
        print(f"OpenAI Error details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ollama/models")
async def get_ollama_models():
    try:
        response = requests.get('http://localhost:11434/api/tags')
        if response.status_code == 200:
            data = response.json()
            print("Ollama API response:", data)  # Debug log
            
            # Extract just the model names from the nested structure
            models = [model['name'] for model in data['models']]
            print("Extracted models:", models)  # Debug log
            
            return {"models": models}
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Ollama API error: {response.text}"
            )
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Ollama models: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to communicate with Ollama: {str(e)}"
        )

@app.post("/api/ollama/chat")
async def ollama_chat(message: OllamaMessage):
    print("Ollama Endpoint hit!")
    try:
        print("Received data:", message.dict())
        
        # Format messages for Ollama
        formatted_messages = []
        for msg in message.messages:
            formatted_msg = {
                "role": msg.role,
                "content": msg.content
            }
            if msg.images:
                # Ollama expects the base64 image data directly
                formatted_msg["images"] = msg.images
            formatted_messages.append(formatted_msg)

        request_data = {
            "model": message.model,
            "messages": formatted_messages
        }
        
        print("Sending to Ollama:", request_data)
        response = ollama.chat(**request_data)
        print("Ollama response:", response)
        
        return {
            'message': response['message']['content'],
            'status': 'success'
        }
    except Exception as e:
        print(f"Ollama Error details: {str(e)}")
        print(f"Error type: {type(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/openai/models")
async def get_openai_models():
    # Return both chat and image models
    models = [
        {"name": "gpt-4o-mini", "type": "chat"},
        {"name": "dall-e-3", "type": "image"}
    ]
    return {"models": models}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)