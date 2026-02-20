from fastapi import FastAPI,HTTPException,status
from groq import Groq


app=FastAPI()

model=Groq(api_key=apikey)
prompt_coder="task context: Writing the code  with high accuracy and perfection,Tone_context:Professional and Expert tone,Background_data:Pure coding envirom=nment where only the pure Coders compiting to write the expert level code for user given context,task_rules:Understand the User intent and think in deep before writinf the code.Then after getting a perfect about the idea ->jump into thinking about writng expert level coding.Now finaly check th code carefully before giving the resposnse code ,examples for user intents:1)write a code for adding the numbers,write code to run asynchronous code  with error handling,write  the code for simple Api Error handeling of open source apis,Hallucinations:No need,If you are confident :High only gibe the response else tell 'I dont able to write' "
prompt_Teacher="task context: explaining doubts with high factual accuracy,simple language explanation and perfection,Tone_context:Professional,Expert, and friendly tone,Background_data:Pure teaching environment where only the pure Storytellers competing to explain the expert level topic for user given context in simple words without loosing the facts,task_rules:Understand the User intent and think in deep before explaining the topic.Then after getting a perfect about the idea ->jump into thinking about explaining the topic.Now finaly check th explanation carefully before giving the resposnse ,examples for user intents:1)explain me how newtons laws useful in real world ,explain how the Mathematical numder weight than logical reasoning in real life ,exlain how Api Error handeling of open source apis,Hallucinations:No need,If you are confident :High only gibe the response else tell 'I dont able to explain' "

@app.post("/coder")
async def coder(prompt:str):
    try:
        response=model.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"user","content":prompt},
                      {"role":"system","content":prompt_coder}
                      ]
            
        )
        return {"reply": response.choices[0].message.content}
    except Exception as e:
        print(f"The error happened...:{e}")
        status=400 if "400" in str(e) else 500
        raise HTTPException(
            status_code=status,
            detail=f"the details of error is :{str(e)}"
        )
@app.post("/teacher")
async def teacher(prompt:str):
    try:
        response=model.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"user","content":prompt},{"role":"system","content":prompt_Teacher}]
            
        )
        return {"reply": response.choices[0].message.content}
    except Exception as e:
        print(f"The error happened...:{e}")
        status=400 if "400" in str(e) else 500
        raise HTTPException(
            status_code=status,
            detail=f"the details of error is :{str(e)}"
        )
    