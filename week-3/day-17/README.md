# 📊 Day 17: Structured Logging & Request Tracking

**Learning Goal:** Master production-grade logging and monitoring techniques

**Time:** 2-3 hours

---

## 🎯 What You'll Learn Today

1. **Structured Logging** - JSON format instead of plain text
2. **Request Tracking** - Correlation IDs across requests
3. **Performance Monitoring** - Timing and metrics
4. **Error Categorization** - Different error levels
5. **Log Analysis** - Querying and analyzing logs

---

## 📁 Project Structure

```
day-17/
├── main.py              # Complete logging demo API
├── requirements.txt     # Dependencies
├── README.md           # This file
├── .env.example        # Environment template
└── logs/               # Generated when you run the app
    ├── app.log         # All logs (JSON format)
    └── error.log       # Errors only (JSON format)
```

---

## 🚀 Quick Start

### Step 1: Setup

```bash
# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Run

```bash
# Run the API
python main.py

# You should see:
# INFO - application_started
# INFO - Starting server...
# Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Test

**Open browser:**
```
http://localhost:8000/docs
```

You'll see the Swagger UI with all endpoints!

---

## 🧪 Testing the Endpoints

### 1. **Health Check** (Normal Logging)

```bash
curl http://localhost:8000/
```

**Expected Response:**
```json
{
  "service": "Day 17: Logging Demo",
  "status": "healthy",
  "request_id": "abc-123-...",
  "timestamp": "2026-03-07T10:30:00Z"
}
```

**Check logs:**
```bash
# Windows PowerShell:
Get-Content logs/app.log -Tail 5

# Mac/Linux:
tail -n 5 logs/app.log
```

**You'll see JSON logs like:**
```json
{
  "timestamp": "2026-03-07T10:30:00Z",
  "level": "INFO",
  "event": "health_check",
  "request_id": "abc-123-...",
  "status": "healthy"
}
```

---

### 2. **Process Data** (Performance Logging)

```bash
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{"data": "test data", "priority": "high"}'
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Processed 9 characters",
  "priority": "high",
  "processing_time_ms": 102.34,
  "request_id": "def-456-..."
}
```

**Check logs - you'll see timing information!**

---

### 3. **Slow Endpoint** (Performance Warning)

```bash
curl "http://localhost:8000/slow?delay_ms=3000"
```

This takes 3 seconds - check logs for **slow_request_detected** warning!

---

### 4. **Error Endpoint** (Error Logging)

```bash
# Trigger validation error
curl "http://localhost:8000/error?error_type=validation"

# Trigger critical error
curl "http://localhost:8000/error?error_type=critical"
```

**Check error.log:**
```bash
Get-Content logs/error.log
```

You'll see detailed error logs with stack traces!

---

### 5. **Analytics** (Metrics)

```bash
curl http://localhost:8000/analytics
```

**Expected Response:**
```json
{
  "total_requests": 15,
  "successful_requests": 12,
  "failed_requests": 3,
  "average_duration_ms": 234.56,
  "success_rate": 80.0
}
```

---

### 6. **Recent Logs** (Log Querying)

```bash
curl "http://localhost:8000/logs/recent?count=5"
```

Returns last 5 log entries as JSON!

---

## 📚 Key Concepts Demonstrated

### 1. **Structured Logging**

**Bad (Plain Text):**
```
INFO: User uploaded file
```

**Good (JSON):**
```json
{
  "timestamp": "2026-03-07T10:30:00Z",
  "level": "INFO",
  "event": "file_uploaded",
  "request_id": "abc-123",
  "user_id": "user456",
  "file_size": 1024000,
  "duration_ms": 234
}
```

**Why Better:**
- Machine-readable
- Searchable by any field
- Can aggregate metrics
- Easy to parse and analyze

---

### 2. **Request IDs**

Every request gets a unique ID:

```
Request 1: request_id = "abc-123"
Request 2: request_id = "def-456"
```

**Benefits:**
- Track entire request flow
- Filter logs for one specific request
- Debug user-specific issues
- Correlate across services

**See it in action:**
```bash
# Make a request
curl http://localhost:8000/

# Response includes:
# "request_id": "abc-123..."

# Filter logs for this request:
Get-Content logs/app.log | Select-String "abc-123"
```

---

### 3. **Log Levels**

| Level | When to Use | Example |
|-------|-------------|---------|
| DEBUG | Development debugging | Variable values |
| INFO | Normal operations | Request completed |
| WARNING | Unexpected but handled | Slow query |
| ERROR | Operation failed | Upload failed |
| CRITICAL | System failure | Out of memory |

**See all levels:**
```bash
# INFO
curl http://localhost:8000/

# WARNING  
curl http://localhost:8000/slow

# ERROR
curl http://localhost:8000/error
```

---

### 4. **Performance Monitoring**

Every request logs:
- Total duration
- Component timing
- Slow request detection

```json
{
  "event": "request_completed",
  "duration_ms": 234.56,
  "is_slow": false
}
```

If duration > 1000ms, you'll see:
```json
{
  "event": "slow_request_detected",
  "duration_ms": 2345.67,
  "threshold_ms": 1000
}
```

---

## 🔍 Log Analysis

### Using PowerShell (Windows)

```powershell
# Get last 10 logs
Get-Content logs/app.log -Tail 10

# Find all errors
Get-Content logs/error.log

# Search for specific event
Get-Content logs/app.log | Select-String "slow_request"

# Count requests
(Get-Content logs/app.log | Select-String "request_completed").Count
```

### Using jq (Mac/Linux)

Install jq first:
```bash
# Mac
brew install jq

# Linux
apt-get install jq
```

Then query:
```bash
# Pretty print last log
tail -n 1 logs/app.log | jq

# Filter by event
cat logs/app.log | jq 'select(.event == "request_completed")'

# Calculate average duration
cat logs/app.log | jq 'select(.event == "request_completed") | .duration_ms' | jq -s 'add/length'

# Find slow requests
cat logs/app.log | jq 'select(.duration_ms > 1000)'

# Count errors by type
cat logs/error.log | jq '.error_type' | sort | uniq -c
```

---

## 📊 Exercises

### Exercise 1: Generate Logs

Make 20 requests to different endpoints:
```bash
# 10 normal requests
for ($i=1; $i -le 10; $i++) { curl http://localhost:8000/ }

# 5 slow requests
for ($i=1; $i -le 5; $i++) { curl "http://localhost:8000/slow?delay_ms=1500" }

# 5 errors
for ($i=1; $i -le 5; $i++) { curl "http://localhost:8000/error?error_type=validation" }
```

### Exercise 2: Analyze Logs

Answer these questions by analyzing logs:

1. How many total requests?
2. How many failed?
3. What's the average request duration?
4. How many slow requests (>1000ms)?
5. What's the most common error type?

### Exercise 3: Track a Request

1. Make a request and note the request_id
2. Find ALL logs for that request_id
3. See the complete request flow

### Exercise 4: Performance Investigation

1. Run analytics endpoint
2. Note the average duration
3. Make 10 slow requests
4. Run analytics again
5. See how average changed

---

## 🎯 Learning Objectives

After completing Day 17, you should be able to:

- [ ] Explain structured logging vs plain text logging
- [ ] Implement JSON logging in FastAPI
- [ ] Add request IDs for tracking
- [ ] Use different log levels appropriately
- [ ] Monitor API performance with logs
- [ ] Categorize and track errors
- [ ] Query and analyze log files
- [ ] Answer interview questions about logging

---

## 💡 Interview Questions

**Q: Why use structured logging instead of plain text?**

A: Structured logging (JSON format) enables:
1. Machine-readable logs for automated analysis
2. Searchable by any field (request_id, user_id, etc.)
3. Easy aggregation of metrics (average duration)
4. Better tooling support (log aggregation systems)
5. Consistent format across services

**Q: What is a request ID and why is it important?**

A: A request ID is a unique identifier for each request. Important because:
1. Tracks request flow across multiple services
2. Correlates all logs for one request
3. Enables debugging of specific user issues
4. Required for distributed tracing
5. Helps identify patterns in failures

**Q: What are the different log levels?**

A: 
- DEBUG: Detailed debugging (development only)
- INFO: Normal operations
- WARNING: Unexpected but handled
- ERROR: Operation failed
- CRITICAL: System failure

Use INFO for production default, ERROR+ for alerts.

---

## 📈 What's Next

**Day 18:** API Rate Limiting & Throttling
**Day 19:** Database Integration for Analytics
**Day 20:** Cloud Deployment (AWS/GCP)

---

## 🎓 Key Takeaways

1. **Logs are for machines, not just humans** - Use JSON
2. **Every request needs an ID** - For tracking
3. **Log levels matter** - Use appropriately
4. **Performance should be logged** - Monitor timing
5. **Errors need context** - Include request_id, user_id, etc.

---

## 🔗 Resources

- [Python JSON Logger](https://github.com/madzak/python-json-logger)
- [FastAPI Logging](https://fastapi.tiangolo.com/tutorial/middleware/)
- [12-Factor App Logs](https://12factor.net/logs)

---

## ✅ Completion Checklist

- [ ] Installed dependencies
- [ ] Run the application
- [ ] Tested all endpoints in Swagger UI
- [ ] Generated logs (app.log, error.log)
- [ ] Analyzed logs with commands
- [ ] Completed all exercises
- [ ] Can explain structured logging
- [ ] Can answer interview questions

---

**Well done on Day 17!** 🎉

You now understand production-level logging - a critical skill that separates junior from senior engineers!

**Commit your work:**
```bash
git add week-3/day-17/
git commit -m "feat(day-17): implement structured logging and request tracking demo

- Create FastAPI logging demonstration
- Implement JSON structured logging
- Add request ID middleware for tracking
- Add performance monitoring with timing
- Demonstrate all log levels (DEBUG-CRITICAL)
- Include log analysis examples
- Add analytics endpoint for metrics

Learned:
- Structured vs plain text logging
- Request correlation with IDs
- Performance monitoring techniques
- Error categorization and tracking
- Log querying and analysis"

git push origin main
```

**Next:** Day 18 - API Rate Limiting! 🚀