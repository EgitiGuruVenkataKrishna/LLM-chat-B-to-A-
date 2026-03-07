"""
Day 17: Structured Logging & Request Tracking Demo
===================================================

A demonstration FastAPI application showcasing:
- Structured JSON logging
- Request ID tracking
- Performance monitoring
- Error categorization
- Log levels
"""

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import logging
import json
import time
import uuid
from datetime import datetime
from pythonjsonlogger import jsonlogger
from pathlib import Path
import sys

# ==================== LOGGING CONFIGURATION ====================

def setup_logging():
    """Configure structured JSON logging"""
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Custom JSON formatter
    class CustomJsonFormatter(jsonlogger.JsonFormatter):
        def add_fields(self, log_record, record, message_dict):
            super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
            
            # Add custom fields
            log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'
            log_record['level'] = record.levelname
            log_record['logger'] = record.name
            log_record['service'] = 'logging-demo'
            
            # Add function and line number for debugging
            if record.levelname in ['ERROR', 'CRITICAL']:
                log_record['function'] = record.funcName
                log_record['line'] = record.lineno
    
    # JSON formatter for file
    json_formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(service)s %(message)s'
    )
    
    # Human-readable formatter for console
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler (human-readable)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    
    # File handler - all logs (JSON)
    file_handler = logging.FileHandler("logs/app.log")
    file_handler.setFormatter(json_formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # File handler - errors only (JSON)
    error_handler = logging.FileHandler("logs/error.log")
    error_handler.setFormatter(json_formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    
    # Silence noisy third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

# Setup logging
logger = setup_logging()

# ==================== REQUEST ID MIDDLEWARE ====================

class RequestIDMiddleware:
    """Middleware to add unique request ID to each request"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Store in scope for access in routes
        scope["request_id"] = request_id
        
        # Track request start time
        start_time = time.time()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Add request ID to response headers
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id.encode()))
                message["headers"] = headers
            await send(message)
        
        await self.app(scope, receive, send_wrapper)

# ==================== FASTAPI APP ====================

app = FastAPI(
    title="Day 17: Logging Demo API",
    description="Demonstrates structured logging and request tracking",
    version="1.0.0"
)

# Add middleware
app.add_middleware(RequestIDMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== PYDANTIC MODELS ====================

class UserData(BaseModel):
    """User input data"""
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    age: int = Field(..., ge=0, le=150)

class ProcessRequest(BaseModel):
    """Request for processing"""
    data: str = Field(..., min_length=1, max_length=1000)
    priority: str = Field(default="normal", regex="^(low|normal|high)$")

class AnalyticsResponse(BaseModel):
    """Analytics data response"""
    total_requests: int
    average_duration_ms: float
    error_count: int
    success_rate: float

# ==================== GLOBAL METRICS ====================

metrics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "total_duration_ms": 0,
    "request_times": []
}

# ==================== HELPER FUNCTIONS ====================

def get_request_id(request: Request) -> str:
    """Extract request ID from request"""
    return request.scope.get("request_id", "unknown")

def log_event(event_name: str, request_id: str, **kwargs):
    """Log an event with structured data"""
    logger.info(
        event_name,
        extra={
            "event": event_name,
            "request_id": request_id,
            **kwargs
        }
    )

def simulate_processing(duration_ms: int):
    """Simulate some processing work"""
    time.sleep(duration_ms / 1000)

# ==================== EVENT HANDLERS ====================

@app.on_event("startup")
async def startup_event():
    """Log application startup"""
    logger.info(
        "application_started",
        extra={
            "event": "startup",
            "service": "logging-demo",
            "version": "1.0.0",
            "environment": "development"
        }
    )

@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown"""
    logger.info(
        "application_shutdown",
        extra={
            "event": "shutdown",
            "total_requests_processed": metrics["total_requests"],
            "success_rate": metrics["successful_requests"] / max(metrics["total_requests"], 1)
        }
    )

# ==================== MIDDLEWARE ====================

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all HTTP requests with performance metrics"""
    
    request_id = get_request_id(request)
    start_time = time.time()
    
    # Log request start
    log_event(
        "request_started",
        request_id,
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else "unknown"
    )
    
    # Update metrics
    metrics["total_requests"] += 1
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        metrics["total_duration_ms"] += duration_ms
        metrics["request_times"].append(duration_ms)
        
        # Keep only last 100 request times
        if len(metrics["request_times"]) > 100:
            metrics["request_times"] = metrics["request_times"][-100:]
        
        # Determine if request was successful
        is_success = 200 <= response.status_code < 400
        
        if is_success:
            metrics["successful_requests"] += 1
        else:
            metrics["failed_requests"] += 1
        
        # Log request completion
        log_level = "info" if is_success else "warning"
        
        log_data = {
            "event": "request_completed",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "is_slow": duration_ms > 1000  # Flag if >1 second
        }
        
        if log_level == "info":
            logger.info("request_completed", extra=log_data)
        else:
            logger.warning("request_completed_with_error", extra=log_data)
        
        # Warn if slow request
        if duration_ms > 1000:
            logger.warning(
                "slow_request_detected",
                extra={
                    "request_id": request_id,
                    "path": request.url.path,
                    "duration_ms": round(duration_ms, 2),
                    "threshold_ms": 1000
                }
            )
        
        return response
        
    except Exception as e:
        # Log request failure
        metrics["failed_requests"] += 1
        
        logger.error(
            "request_failed",
            extra={
                "event": "request_failed",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "error": str(e),
                "error_type": type(e).__name__
            },
            exc_info=True
        )
        
        raise

# ==================== ENDPOINTS ====================

@app.get("/")
async def root(request: Request):
    """Root endpoint - health check"""
    request_id = get_request_id(request)
    
    log_event(
        "health_check",
        request_id,
        status="healthy"
    )
    
    return {
        "service": "Day 17: Logging Demo",
        "status": "healthy",
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat() + 'Z'
    }

@app.post("/process")
async def process_data(request: Request, data: ProcessRequest):
    """
    Process some data (demonstrates normal logging)
    
    This endpoint:
    - Logs the processing start
    - Simulates work
    - Logs completion with timing
    """
    request_id = get_request_id(request)
    start_time = time.time()
    
    log_event(
        "processing_started",
        request_id,
        data_length=len(data.data),
        priority=data.priority
    )
    
    # Simulate processing based on priority
    processing_time = {
        "low": 500,
        "normal": 300,
        "high": 100
    }
    
    simulate_processing(processing_time[data.priority])
    
    duration_ms = (time.time() - start_time) * 1000
    
    log_event(
        "processing_completed",
        request_id,
        duration_ms=round(duration_ms, 2),
        priority=data.priority,
        data_length=len(data.data)
    )
    
    return {
        "status": "success",
        "message": f"Processed {len(data.data)} characters",
        "priority": data.priority,
        "processing_time_ms": round(duration_ms, 2),
        "request_id": request_id
    }

@app.post("/user")
async def create_user(request: Request, user: UserData):
    """
    Create a user (demonstrates validation logging)
    
    Shows:
    - Input validation
    - Success logging
    - Data sanitization (don't log sensitive data)
    """
    request_id = get_request_id(request)
    
    log_event(
        "user_creation_started",
        request_id,
        user_name=user.name,
        # DON'T log email in production! Shown for demo only
        user_age=user.age
    )
    
    # Simulate user creation
    simulate_processing(200)
    
    user_id = str(uuid.uuid4())[:8]
    
    log_event(
        "user_created",
        request_id,
        user_id=user_id,
        user_name=user.name
    )
    
    return {
        "status": "success",
        "user_id": user_id,
        "message": f"User {user.name} created successfully",
        "request_id": request_id
    }

@app.get("/slow")
async def slow_endpoint(request: Request, delay_ms: int = 2000):
    """
    Intentionally slow endpoint (demonstrates performance logging)
    
    Args:
        delay_ms: Delay in milliseconds (default: 2000)
    
    This will trigger slow request warnings!
    """
    request_id = get_request_id(request)
    
    logger.warning(
        "slow_endpoint_called",
        extra={
            "event": "slow_endpoint_called",
            "request_id": request_id,
            "requested_delay_ms": delay_ms,
            "warning": "This endpoint is intentionally slow for demo"
        }
    )
    
    simulate_processing(delay_ms)
    
    return {
        "message": f"Completed after {delay_ms}ms delay",
        "request_id": request_id
    }

@app.get("/error")
async def error_endpoint(request: Request, error_type: str = "general"):
    """
    Intentionally cause errors (demonstrates error logging)
    
    Args:
        error_type: Type of error to trigger (general, validation, critical)
    
    This shows different error levels and categorization!
    """
    request_id = get_request_id(request)
    
    logger.warning(
        "error_endpoint_called",
        extra={
            "event": "error_endpoint_called",
            "request_id": request_id,
            "error_type": error_type
        }
    )
    
    if error_type == "validation":
        logger.error(
            "validation_error_triggered",
            extra={
                "event": "validation_error",
                "request_id": request_id,
                "error_category": "user_error"
            }
        )
        raise HTTPException(status_code=400, detail="Validation failed (demo)")
    
    elif error_type == "critical":
        logger.critical(
            "critical_error_triggered",
            extra={
                "event": "critical_error",
                "request_id": request_id,
                "error_category": "system_error",
                "requires_immediate_attention": True
            }
        )
        raise HTTPException(status_code=500, detail="Critical system error (demo)")
    
    else:
        logger.error(
            "general_error_triggered",
            extra={
                "event": "general_error",
                "request_id": request_id,
                "error_category": "application_error"
            }
        )
        raise HTTPException(status_code=500, detail="Internal server error (demo)")

@app.get("/analytics")
async def get_analytics(request: Request):
    """
    Get analytics about API usage
    
    Shows how to use logs for metrics and analytics
    """
    request_id = get_request_id(request)
    
    # Calculate metrics
    avg_duration = (
        metrics["total_duration_ms"] / metrics["total_requests"]
        if metrics["total_requests"] > 0
        else 0
    )
    
    success_rate = (
        metrics["successful_requests"] / metrics["total_requests"]
        if metrics["total_requests"] > 0
        else 0
    )
    
    analytics_data = {
        "total_requests": metrics["total_requests"],
        "successful_requests": metrics["successful_requests"],
        "failed_requests": metrics["failed_requests"],
        "average_duration_ms": round(avg_duration, 2),
        "success_rate": round(success_rate * 100, 2),
        "request_id": request_id
    }
    
    log_event(
        "analytics_requested",
        request_id,
        **analytics_data
    )
    
    return analytics_data

@app.get("/logs/recent")
async def get_recent_logs(request: Request, count: int = 10):
    """
    Get recent log entries (demonstrates log querying)
    
    Args:
        count: Number of recent logs to return
    
    In production, you'd query from a log aggregation system
    """
    request_id = get_request_id(request)
    
    try:
        # Read last N lines from log file
        with open("logs/app.log", "r") as f:
            lines = f.readlines()
            recent_lines = lines[-count:]
            
            # Parse JSON logs
            recent_logs = []
            for line in recent_lines:
                try:
                    log_entry = json.loads(line.strip())
                    recent_logs.append(log_entry)
                except json.JSONDecodeError:
                    continue
        
        log_event(
            "logs_retrieved",
            request_id,
            log_count=len(recent_logs)
        )
        
        return {
            "count": len(recent_logs),
            "logs": recent_logs,
            "request_id": request_id
        }
        
    except FileNotFoundError:
        logger.error(
            "log_file_not_found",
            extra={
                "request_id": request_id,
                "file": "logs/app.log"
            }
        )
        raise HTTPException(status_code=404, detail="No logs available yet")

@app.delete("/logs/clear")
async def clear_logs(request: Request):
    """
    Clear log files (demonstrates log management)
    
    WARNING: Only for development/testing!
    """
    request_id = get_request_id(request)
    
    logger.warning(
        "logs_cleared",
        extra={
            "event": "logs_cleared",
            "request_id": request_id,
            "warning": "This should not be used in production"
        }
    )
    
    # Clear log files
    try:
        with open("logs/app.log", "w") as f:
            f.write("")
        with open("logs/error.log", "w") as f:
            f.write("")
        
        return {
            "status": "success",
            "message": "Logs cleared",
            "request_id": request_id
        }
    except Exception as e:
        logger.error(
            "log_clear_failed",
            extra={
                "request_id": request_id,
                "error": str(e)
            },
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to clear logs")

# ==================== RUN ====================

if __name__ == "__main__":
    import uvicorn
    
    logger.info(
        "starting_server",
        extra={
            "event": "server_start",
            "host": "0.0.0.0",
            "port": 8000
        }
    )
    
    uvicorn.run(app, host="0.0.0.0", port=8000)