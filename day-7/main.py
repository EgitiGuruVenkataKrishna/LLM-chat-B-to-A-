"""
LLM Chat API
A FastAPI backend that integrates with OpenAI API to provide AI-powered chat responses.
Author: Guru Venkata Krishna
Day: 7/39 of AI Systems Engineer Challenge
"""

import logging
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq

# Loading env variables
load_dotenv()

#logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


app = FastAPI(
    title="LLM Chat API",
    description="REST API for AI-powered chat using Groq...",
    version="1.0.0"
)

modal=Groq(api_key=os.getenv("apikey"))


# Request Models classes using pydantic BaseModel
class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str
    temperature: float = 0.7
    max_tokens: int = 500

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str
    tokens_used: int

# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    logger.info("Health check called")
    return {"status": "healthy", "message": "LLM Chat API is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint that processes user messages and returns AI responses.
    
    Args:
     request: ChatRequest containing user message and parameters
    
    Returns:
       ChatResponse with AI-generated response and token usage
    
    Raises:
        HTTPException: If API call fails
    """
    logger.info(f"Received chat request: {request.message[:50]}...")
    
    try:
        # Calling Groq API
        response = modal.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": request.message}
            ],
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        #response
        ai_message = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        logger.info(f"Chat successful. Tokens used: {tokens_used}")
        
        return ChatResponse(
            response=ai_message,
            tokens_used=tokens_used
        )
        
    except Exception as e:
        logger.error(f"Chat failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"API call failed: {str(e)}")
    
prompt_coder="task context: Writing the code  with high accuracy and perfection,Tone_context:Professional and Expert tone,Background_data:Pure coding envirom=nment where only the pure Coders compiting to write the expert level code for user given context,task_rules:Understand the User intent and think in deep before writinf the code.Then after getting a perfect about the idea ->jump into thinking about writng expert level coding.Now finaly check th code carefully before giving the resposnse code ,examples for user intents:1)write a code for adding the numbers,write code to run asynchronous code  with error handling,write  the code for simple Api Error handeling of open source apis,Hallucinations:No need,If you are confident :High only gibe the response else tell 'I dont able to write' "

@app.post("/chat/coder")
async def chat_coder(request: ChatRequest):
    """Chat endpoint with coding assistant persona"""
    try:
        # Calling Groq API for code generation persona
        response = modal.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": prompt_coder},
                {"role": "user", "content": request.message}
            ],
            temperature=0.4,
            max_tokens=request.max_tokens
        )
        
        #response
        ai_message = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        logger.info(f"Chat successful. Tokens used: {tokens_used}")
        
        return ChatResponse(
            response=ai_message,
            tokens_used=tokens_used
        )
        
    except Exception as e:
        logger.error(f"code generation chat failed: {str(e)}")
        status=400 if "400" in str(e) else 500
        raise HTTPException(status_code=status, detail=f"API call failed: {str(e)}")
    

prompt_Teacher="task context: explaining doubts with high factual accuracy,simple language explanation and perfection,Tone_context:Professional,Expert, and friendly tone,Background_data:Pure teaching environment where only the pure Storytellers competing to explain the expert level topic for user given context in simple words without loosing the facts,task_rules:Understand the User intent and think in deep before explaining the topic.Then after getting a perfect about the idea ->jump into thinking about explaining the topic.Now finaly check th explanation carefully before giving the resposnse ,examples for user intents:1)explain me how newtons laws useful in real world ,explain how the Mathematical numder weight than logical reasoning in real life ,exlain how Api Error handeling of open source apis,Hallucinations:No need,If you are confident :High only gibe the response else tell 'I dont able to explain' "


@app.post("/chat/teacher")
async def chat_teacher(request: ChatRequest):
    """Chat endpoint with teacher persona"""
    try:
        # Calling Groq API for explaining a typical topic
        response = modal.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": prompt_Teacher},
                {"role": "user", "content": request.message}
            ],
            temperature=0.8,
            max_tokens=request.max_tokens
        )
        
        #response
        ai_message = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        logger.info(f"Explanation successful. Tokens used: {tokens_used}")
        
        return ChatResponse(
            response=ai_message,
            tokens_used=tokens_used
        )
        
    except Exception as e:
        logger.error(f"Explanation failed: {str(e)}")
        status=400 if "400" in str(e) else 500
        raise HTTPException(status_code=status, detail=f"API call failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)