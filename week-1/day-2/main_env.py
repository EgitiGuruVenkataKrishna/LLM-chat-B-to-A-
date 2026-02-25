from fastapi import FastAPI,Depends,HTTPException,status
from pydantic import BaseModel
from pydantic_settings import BaseSettings,SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    app_name:str
    secret_api_key:str
    model_config=SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings():
    return Settings()

class Dolls(BaseModel):
    doll_id:int
    doll_name:str
    quantity:int
    price:float

app=FastAPI()

@app.post("/doll")
async def create_order(doll:Dolls,api_key:str,settings:Settings=Depends(get_settings)):
    if api_key!=settings.secret_api_key:
        raise HTTPException (status_code=403,detail="Invalid API key...")
    
    total=doll.quantity*doll.price
    return{
        "msg":f"Doll order received for {settings.app_name}",
        "order_details":doll,
        "total_cost":total

    }




