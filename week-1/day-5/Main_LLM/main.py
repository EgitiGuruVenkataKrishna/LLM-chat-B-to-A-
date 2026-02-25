import logging
from fastapi import FastAPI

# Configure logging at the top of your file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_1.log'),
        logging.StreamHandler()
    ]
)

app = FastAPI()

@app.post("/chat")
async def chat(message: str):
    logging.info(f"Received message: {message}")  # Log what user sent
    
    try:
        # Your LLM API call here
        response = "AI response"
        logging.info("LLM API call successful")  # Log success
        return {"response": response}
    
    except Exception as e:
        logging.error(f"LLM API call failed: {e}")  # Log errors
        return {"error": "Something went wrong"}



