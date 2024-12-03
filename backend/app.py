#!/usr/bin/env python3
"""
FastAPI backend server for AI chat application.

This module provides REST API endpoints for interacting with OpenAI and Ollama models.
It handles chat conversations, image generation, and model management.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
from openai import OpenAI
import os
from dotenv import load_dotenv
import ollama
import requests

# Load OpenAI API key from environment file
load_dotenv('openai.env')

# Initialize FastAPI application
app = FastAPI()

# Configure CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client with API key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def sanitize_message(content: str) -> str:
    """Sanitize and optimize message content for AI processing.
    
    Performs the following operations:
    1. Normalizes whitespace and removes redundant spaces
    2. Removes problematic characters and normalizes punctuation
    3. Trims excessive newlines and spaces
    4. Normalizes quotes and apostrophes
    5. Ensures proper sentence spacing
    
    Args:
        content (str): Raw message content to sanitize
        
    Returns:
        str: Sanitized and normalized message content
    """
    if not content:
        return ""
    
    # Normalize whitespace and remove redundant spaces
    content = ' '.join(content.split())
    
    # Replace problematic characters
    replacements = {
        '…': '...',  # Normalize ellipsis
        '"': '"',    # Normalize quotes
        '"': '"',
        ''': "'",    # Normalize apostrophes
        ''': "'",
        '—': '-',    # Normalize dashes
        '–': '-',
        '´': "'",    # Additional quote normalization
        '`': "'",
        '\u200b': '', # Remove zero-width spaces
        '\ufeff': '', # Remove byte order marks
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    # Ensure proper sentence spacing
    content = content.replace('.', '. ').replace('!', '! ').replace('?', '? ')
    
    # Remove multiple periods (except for ellipsis)
    while '....' in content:
        content = content.replace('....', '...')
    
    # Clean up spaces around punctuation
    content = content.replace(' ,', ',').replace(' .', '.').replace(' !', '!').replace(' ?', '?')
    
    # Ensure proper spacing after punctuation
    for punct in ['.', ',', '!', '?', ':', ';']:
        content = content.replace(f'{punct}', f'{punct} ')
    
    # Remove multiple spaces (again, in case previous operations created any)
    content = ' '.join(content.split())
    
    # Strip leading/trailing whitespace
    content = content.strip()
    
    return content

class Message(BaseModel):
    """Pydantic model for chat messages."""
    role: str
    content: str
    model: Optional[str] = None
    images: Optional[List[str]] = None

class OllamaMessage(BaseModel):
    """Pydantic model for Ollama-specific chat requests."""
    messages: List[Message]
    model: str

class ChatRequest(BaseModel):
    """Pydantic model for general chat requests."""
    messages: List[Message]
    model: str

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Handle chat requests for both text and image generation.
    
    Supports OpenAI's GPT models and DALL-E for image generation.
    
    Args:
        request (ChatRequest): The chat request containing messages and model selection
        
    Returns:
        dict: Response containing generated message or image URL
        
    Raises:
        HTTPException: If model is unsupported or API call fails
    """
    print("OpenAI Endpoint hit!")
    try:
        print("Received request data:", request.dict())
        
        if request.model == "dall-e-3":
            # Sanitize the prompt for DALL-E
            sanitized_prompt = sanitize_message(request.messages[-1].content)
            response = client.images.generate(
                model="dall-e-3",
                prompt=sanitized_prompt,
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
        
        # Sanitize all messages
        formatted_messages = [
            {
                "role": msg.role,
                "content": sanitize_message(msg.content)
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
    """Fetch available models from local Ollama instance.
    
    Returns:
        dict: List of available Ollama models
        
    Raises:
        HTTPException: If unable to communicate with Ollama service
    """
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
    """Handle chat requests for Ollama models.
    
    Supports both text and vision models.
    
    Args:
        message (OllamaMessage): Chat request containing messages and model selection
        
    Returns:
        dict: Response containing generated message
        
    Raises:
        HTTPException: If Ollama API call fails
    """
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
    """Get list of supported OpenAI models.
    
    Returns:
        dict: List of supported models with their types
    """
    # Return both chat and image models
    models = [
        {"name": "gpt-4o-mini", "type": "chat"},
        {"name": "dall-e-3", "type": "image"}
    ]
    return {"models": models}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)