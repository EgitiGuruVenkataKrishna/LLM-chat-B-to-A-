from fastapi import FastAPI,HTTPException
from groq import Groq
import os

app=FastAPI()

api_key=os.getenv("GROQ_API_KEY")
model=Groq(api_key=api_key)

@app.post("/Try_ai")
async def Try_ai(prompt:str):
    try:
        responses=model.chat.completions.create(
            model='llama-3.1-8b-instant',
            messages=[{"role":"user","content":prompt}]

        )
        return {f"reply: {responses.choices[0].message.content}"}
    except Exception as e:
        print(f"Error in calling GroqAPI:{str(e)}")
        
        status=401 if "401" in str(e) else 500
        raise HTTPException(
            status_code=status,
            details=f"the details of error is :{str(e)}"
        )
    
