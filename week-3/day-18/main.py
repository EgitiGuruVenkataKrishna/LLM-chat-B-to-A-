"""
Day 18: API Rate Limiting & Security
=====================================

Learn how to protect your API from abuse by limiting requests.

SIMPLE CONCEPT:
- Like a bouncer at a club: "You can only enter 5 times per minute"
- Prevents one user from overwhelming your API
- Protects your server from crashes
"""

from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import time
from collections import defaultdict
from datetime import datetime, timedelta
import hashlib

# ==================== CONFIGURATION ====================

# Rate limit rules
RATE_LIMITS = {
    "anonymous": {
        "requests_per_minute": 5,
        "requests_per_hour": 50
    },
    "authenticated": {
        "requests_per_minute": 20,
        "requests_per_hour": 500
    },
    "premium": {
        "requests_per_minute": 100,
        "requests_per_hour": 5000
    }
}

# ==================== IN-MEMORY STORAGE ====================

# Store request counts per user
# In production: Use Redis instead!
request_counts = defaultdict(lambda: {
    "minute": {"count": 0, "reset_time": time.time() + 60},
    "hour": {"count": 0, "reset_time": time.time() + 3600}
})

# Store API keys (fake database)
# In production: Use real database!
API_KEYS = {
    "test-key-123": {"user": "john", "tier": "authenticated"},
    "premium-key-456": {"user": "mary", "tier": "premium"}
}

# ==================== FASTAPI APP ====================

app = FastAPI(
    title="Day 18: Rate Limiting Demo",
    description="Learn how to protect your API with rate limits",
    version="1.0.0"
)

# ==================== HELPER FUNCTIONS ====================

def get_client_identifier(request: Request, api_key: Optional[str] = None) -> tuple[str, str]:
    """
    Identify the client making the request
    
    Returns:
        (identifier, tier)
        - identifier: Unique ID for this client
        - tier: "anonymous", "authenticated", or "premium"
    """
    if api_key and api_key in API_KEYS:
        # User has valid API key
        user_data = API_KEYS[api_key]
        return f"user:{user_data['user']}", user_data["tier"]
    else:
        # Anonymous user - identify by IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}", "anonymous"

def check_rate_limit(identifier: str, tier: str) -> tuple[bool, dict]:
    """
    Check if user has exceeded rate limit
    
    Returns:
        (allowed, info)
        - allowed: True if request is allowed, False if blocked
        - info: Dictionary with rate limit info
    """
    current_time = time.time()
    limits = RATE_LIMITS[tier]
    user_data = request_counts[identifier]
    
    # Check minute limit
    if current_time > user_data["minute"]["reset_time"]:
        # Reset minute counter
        user_data["minute"]["count"] = 0
        user_data["minute"]["reset_time"] = current_time + 60
    
    # Check hour limit
    if current_time > user_data["hour"]["reset_time"]:
        # Reset hour counter
        user_data["hour"]["count"] = 0
        user_data["hour"]["reset_time"] = current_time + 3600
    
    # Check if limits exceeded
    minute_exceeded = user_data["minute"]["count"] >= limits["requests_per_minute"]
    hour_exceeded = user_data["hour"]["count"] >= limits["requests_per_hour"]
    
    if minute_exceeded or hour_exceeded:
        # Rate limit exceeded!
        return False, {
            "allowed": False,
            "tier": tier,
            "limit_per_minute": limits["requests_per_minute"],
            "limit_per_hour": limits["requests_per_hour"],
            "used_this_minute": user_data["minute"]["count"],
            "used_this_hour": user_data["hour"]["count"],
            "reset_in_seconds": int(user_data["minute"]["reset_time"] - current_time)
        }
    
    # Request allowed!
    user_data["minute"]["count"] += 1
    user_data["hour"]["count"] += 1
    
    return True, {
        "allowed": True,
        "tier": tier,
        "limit_per_minute": limits["requests_per_minute"],
        "limit_per_hour": limits["requests_per_hour"],
        "remaining_this_minute": limits["requests_per_minute"] - user_data["minute"]["count"],
        "remaining_this_hour": limits["requests_per_hour"] - user_data["hour"]["count"],
        "reset_in_seconds": int(user_data["minute"]["reset_time"] - current_time)
    }

# ==================== MIDDLEWARE ====================

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """
    Check rate limits for every request
    """
    # Skip rate limiting for docs
    if request.url.path in ["/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)
    
    # Get API key from header
    api_key = request.headers.get("X-API-Key")
    
    # Identify client
    identifier, tier = get_client_identifier(request, api_key)
    
    # Check rate limit
    allowed, info = check_rate_limit(identifier, tier)
    
    if not allowed:
        # Rate limit exceeded!
        return JSONResponse(
            status_code=429,  # 429 = Too Many Requests
            content={
                "error": "Rate limit exceeded",
                "message": f"You can make {info['limit_per_minute']} requests per minute",
                "tier": info["tier"],
                "retry_after_seconds": info["reset_in_seconds"]
            },
            headers={
                "X-RateLimit-Limit": str(info["limit_per_minute"]),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(info["reset_in_seconds"]),
                "Retry-After": str(info["reset_in_seconds"])
            }
        )
    
    # Request allowed - process it
    response = await call_next(request)
    
    # Add rate limit info to response headers
    response.headers["X-RateLimit-Limit"] = str(info["limit_per_minute"])
    response.headers["X-RateLimit-Remaining"] = str(info["remaining_this_minute"])
    response.headers["X-RateLimit-Reset"] = str(info["reset_in_seconds"])
    
    return response

# ==================== PYDANTIC MODELS ====================

class DataRequest(BaseModel):
    data: str

class ApiKeyRequest(BaseModel):
    username: str

# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    """
    Basic endpoint - no authentication needed
    Rate limit: 5 requests/minute for anonymous users
    """
    return {
        "message": "Welcome to Rate Limiting Demo!",
        "info": "Try making requests and watch the rate limits",
        "tiers": {
            "anonymous": "5 req/min, 50 req/hour (no API key)",
            "authenticated": "20 req/min, 500 req/hour (use API key: test-key-123)",
            "premium": "100 req/min, 5000 req/hour (use API key: premium-key-456)"
        }
    }

@app.get("/public")
async def public_endpoint():
    """
    Public endpoint anyone can access
    But still rate limited!
    """
    return {
        "message": "This is a public endpoint",
        "data": "Anyone can access this",
        "note": "But you're still rate limited based on your tier"
    }

@app.post("/process")
async def process_data(data: DataRequest):
    """
    Process some data
    Rate limited based on your tier
    """
    return {
        "message": "Data processed successfully",
        "input": data.data,
        "length": len(data.data)
    }

@app.get("/protected")
async def protected_endpoint(api_key: Optional[str] = Header(None, alias="X-API-Key")):
    """
    Protected endpoint - requires API key
    
    Try with:
    - No key: Rate limited to 5 req/min
    - test-key-123: Rate limited to 20 req/min
    - premium-key-456: Rate limited to 100 req/min
    """
    if not api_key or api_key not in API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )
    
    user_data = API_KEYS[api_key]
    
    return {
        "message": "Access granted to protected resource",
        "user": user_data["user"],
        "tier": user_data["tier"],
        "data": "This is sensitive data only for authenticated users"
    }

@app.get("/rate-limit-status")
async def rate_limit_status(
    request: Request,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Check your current rate limit status
    """
    identifier, tier = get_client_identifier(request, api_key)
    user_data = request_counts[identifier]
    limits = RATE_LIMITS[tier]
    current_time = time.time()
    
    return {
        "identifier": identifier,
        "tier": tier,
        "limits": {
            "per_minute": limits["requests_per_minute"],
            "per_hour": limits["requests_per_hour"]
        },
        "usage": {
            "this_minute": user_data["minute"]["count"],
            "this_hour": user_data["hour"]["count"]
        },
        "remaining": {
            "this_minute": limits["requests_per_minute"] - user_data["minute"]["count"],
            "this_hour": limits["requests_per_hour"] - user_data["hour"]["count"]
        },
        "reset_in_seconds": {
            "minute": int(user_data["minute"]["reset_time"] - current_time),
            "hour": int(user_data["hour"]["reset_time"] - current_time)
        }
    }

@app.post("/get-api-key")
async def get_api_key(request: ApiKeyRequest):
    """
    Get a demo API key (normally this would require real authentication)
    
    This is just for demo! In production:
    - User would sign up
    - Verify email
    - Payment (for premium)
    - Generate real secure key
    """
    # Generate a fake API key
    key = f"demo-{hashlib.md5(request.username.encode()).hexdigest()[:16]}"
    
    # Add to our "database"
    API_KEYS[key] = {
        "user": request.username,
        "tier": "authenticated"
    }
    
    return {
        "message": "API key created (demo only!)",
        "api_key": key,
        "tier": "authenticated",
        "limits": {
            "per_minute": RATE_LIMITS["authenticated"]["requests_per_minute"],
            "per_hour": RATE_LIMITS["authenticated"]["requests_per_hour"]
        },
        "usage": "Add header: X-API-Key: {your-key}"
    }

@app.get("/stats")
async def get_stats():
    """
    View overall API usage statistics
    """
    total_users = len(request_counts)
    
    tier_counts = {"anonymous": 0, "authenticated": 0, "premium": 0}
    for identifier in request_counts.keys():
        if identifier.startswith("ip:"):
            tier_counts["anonymous"] += 1
        else:
            # Check tier from API_KEYS
            for key, data in API_KEYS.items():
                if f"user:{data['user']}" == identifier:
                    tier_counts[data["tier"]] += 1
                    break
    
    return {
        "total_users": total_users,
        "users_by_tier": tier_counts,
        "total_api_keys": len(API_KEYS),
        "rate_limits": RATE_LIMITS
    }

# ==================== ERROR HANDLERS ====================

@app.exception_handler(429)
async def rate_limit_handler(request: Request, exc: HTTPException):
    """
    Custom error page for rate limit exceeded
    """
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate Limit Exceeded",
            "message": "You've made too many requests. Please slow down!",
            "help": "Check response headers for X-RateLimit-* info",
            "upgrade": "Get higher limits with an API key (use /get-api-key)"
        }
    )

# ==================== STARTUP ====================

@app.on_event("startup")
async def startup_event():
    """
    Print info on startup
    """
    print("\n" + "="*60)
    print("🚀 DAY 18: RATE LIMITING API")
    print("="*60)
    print("\n📚 RATE LIMITS:")
    for tier, limits in RATE_LIMITS.items():
        print(f"  {tier.upper():12} - {limits['requests_per_minute']} req/min, {limits['requests_per_hour']} req/hour")
    
    print("\n🔑 TEST API KEYS:")
    print("  test-key-123     - Authenticated tier")
    print("  premium-key-456  - Premium tier")
    
    print("\n💡 TRY THIS:")
    print("  1. Visit http://localhost:8000/docs")
    print("  2. Make 6 requests to / (you'll get rate limited!)")
    print("  3. Try with API key: X-API-Key: test-key-123")
    print("  4. Check your status: /rate-limit-status")
    print("\n" + "="*60 + "\n")

# ==================== RUN ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)