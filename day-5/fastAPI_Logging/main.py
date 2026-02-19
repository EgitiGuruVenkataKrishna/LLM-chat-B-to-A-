from fastapi import FastAPI,HTTPException,Request
from typing import Dict
from logger import logger


app=FastAPI()
logger.info("Starting API...")

@app.middleware("http")
async def log_middleware(request:Request,call_next):
    log_dict={'url':request.url.path,
              'method':request.method
    }
    logger.info(log_dict)

    response=await call_next(request)
    return response



@app.get("/" or "/Home")
async def Home():
    #logger.info("Request to Home page")
    return {"Welcome to FastApi_Home Screen"}

@app.get("/upload-Audio")
async def upload_Audio()->Dict:
    #logger.info("Request for the Audio upload page...")
    return {"msg":"UPLOAD Finished...."}

