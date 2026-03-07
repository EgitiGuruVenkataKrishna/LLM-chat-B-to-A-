from fastapi import FastAPI, Response
from prometheus_client import generate_latest
from metrics import REQUEST_COUNT, REQUEST_TIME, ERROR_COUNT
from logging_config import get_logger
import time

app = FastAPI()
logger = get_logger()
@app.get("/generate")
def generate():
    global success, total, tokens_used

    start = time.time()
    total += 1

    try:
        tokens = 50
        tokens_used += tokens
        time.sleep(0.1)

        success += 1
        REQUEST_COUNT.inc()

        duration = time.time() - start
        REQUEST_TIME.observe(duration)

        logger.info({
            "endpoint": "/generate",
            "tokens_used": tokens,
            "request_time_ms": duration * 1000,
            "status": "success"
        })

        return {"result": "hello"}

    except Exception as e:

        ERROR_COUNT.inc()

        logger.error({
            "endpoint": "/generate",
            "error": str(e)
        })

        return {"error": "failed"}
    
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
@app.get("/metrics")
def metrics():        
    return Response(generate_latest(), media_type="text/plain")

success = 0
total = 0
tokens_used = 0