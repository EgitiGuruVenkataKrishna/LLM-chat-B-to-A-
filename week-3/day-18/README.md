# 🛡️ DAY 18: API Rate Limiting

**Simple Goal:** Stop users from making too many requests and crashing your server.

**Real-World Example:** Like a bouncer at a club - "You can only enter 5 times per hour"

**Time:** 2 hours

---

## 🎯 THE PROBLEM

**Without rate limiting:**
```
User makes 1,000 requests per second → Your server crashes 💥
OR
Hacker tries to break in by guessing passwords → 10,000 attempts/second
OR
Someone uses your expensive AI API for free → Your bill is $10,000
```

**With rate limiting:**
```
User makes 6th request → "Sorry, you can only make 5 requests per minute"
Hacker tries password guessing → Blocked after 3 attempts
Free tier user → Limited to 50 requests/hour
```

---

## 📚 WHAT WE'LL LEARN

**1. Rate Limiting** - "You can only do X requests per minute"
**2. API Keys** - "Who are you? Show me your key"
**3. Tiers** - "Free users: 5/min, Paid users: 100/min"

That's it! Just 3 simple concepts.

---

## 🚀 QUICK START

### Step 1: Setup
```bash
# Create folder
mkdir week-3\day-18
cd week-3\day-18

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install
pip install -r requirements.txt
```

### Step 2: Run
```bash
python main.py
```

we'll see:
```
🚀 DAY 18: RATE LIMITING API
📚 RATE LIMITS:
  ANONYMOUS    - 5 req/min, 50 req/hour
  AUTHENTICATED- 20 req/min, 500 req/hour
  PREMIUM      - 100 req/min, 5000 req/hour
```

### Step 3: Test
Open browser: **http://localhost:8000/docs**

---

## 🧪 SIMPLE TESTS

### Test 1: Get Rate Limited!

**Open browser console (F12), paste this:**
```javascript
// Make 6 requests (limit is 5)
for(let i = 0; i < 6; i++) {
    fetch('http://localhost:8000/public')
        .then(r => r.json())
        .then(data => console.log(`Request ${i+1}:`, data))
        .catch(err => console.log(`Request ${i+1} BLOCKED:`, err));
}
```

**What happens:**
- Requests 1-5: ✅ Success
- Request 6: ❌ **429 Too Many Requests**

**You just got rate limited!** 🎉

---

### Test 2: Check Your Status

**Visit:** http://localhost:8000/rate-limit-status

**You'll see:**
```json
{
  "tier": "anonymous",
  "limits": {
    "per_minute": 5,
    "per_hour": 50
  },
  "usage": {
    "this_minute": 6
  },
  "remaining": {
    "this_minute": 0  ← You're blocked!
  },
  "reset_in_seconds": 45  ← Wait 45 seconds!
}
```

---

### Test 3: Use an API Key (Get Higher Limits)

**In Swagger UI (http://localhost:8000/docs):**

1. Find `/public` endpoint
2. Click "Try it out"
3. Click "Execute" **5 times** → Last one gets blocked!
4. Now click the **🔓 Authorize** button at top
5. Enter API Key: `test-key-123`
6. Click "Authorize"
7. Try again - now you can make **20 requests per minute!** ✅

---

## 📖 HOW IT WORKS (Simple Explanation)

### Concept 1: Counting Requests

**Like counting customers entering a store:**

```python
# Simple counter
visitor_count = 0

def enter_store():
    visitor_count += 1
    
    if visitor_count > 5:
        return "Sorry, store is full!"
    
    return "Welcome!"
```

**Same for API:**
```python
request_count = 0

def handle_request():
    request_count += 1
    
    if request_count > 5:
        return "Rate limit exceeded!"
    
    return "Success!"
```

---

### Concept 2: Time Windows

**Problem:** Counter keeps growing forever!

**Solution:** Reset every minute

```python
import time

data = {
    "count": 0,
    "reset_time": time.time() + 60  # Reset in 60 seconds
}

def handle_request():
    current_time = time.time()
    
    # Time to reset?
    if current_time > data["reset_time"]:
        data["count"] = 0
        data["reset_time"] = current_time + 60
    
    # Check limit
    if data["count"] >= 5:
        return "Too many requests! Try again later"
    
    data["count"] += 1
    return "Success!"
```

**That's the core idea!** ✅

---

### Concept 3: Different Users Get Different Limits

```python
LIMITS = {
    "free": 5,      # Free users: 5 req/min
    "paid": 100     # Paid users: 100 req/min
}

def handle_request(user_tier):
    # Check their specific limit
    limit = LIMITS[user_tier]
    
    if count > limit:
        return "Rate limit exceeded!"
```

---

## 🎯 THE 3 TIERS

| Tier | Limit/Min | Limit/Hour | How to Get |
|------|-----------|------------|------------|
| **Anonymous** | 5 | 50 | No API key needed |
| **Authenticated** | 20 | 500 | Use API key: `test-key-123` |
| **Premium** | 100 | 5000 | Use API key: `premium-key-456` |

---

## 🔑 API KEYS EXPLAINED

**What:** A secret password that identifies you

**Why:** So the API knows who you are and what limits to apply

**How to use:**

**Option 1: In Header (Recommended)**
```bash
curl http://localhost:8000/protected \
  -H "X-API-Key: test-key-123"
```

**Option 2: In Swagger UI**
1. Click 🔓 "Authorize" button
2. Enter: `test123`
3. All your requests now use this key!

---

## 📊 UNDERSTANDING RESPONSE HEADERS

**Every response includes rate limit info in headers:**

```http
X-RateLimit-Limit: 5        ← Your limit per minute
X-RateLimit-Remaining: 2    ← Requests left
X-RateLimit-Reset: 45       ← Seconds until reset
```

**In browser console:**
```javascript
fetch('http://localhost:8000/public')
    .then(response => {
        console.log('Limit:', response.headers.get('X-RateLimit-Limit'));
        console.log('Remaining:', response.headers.get('X-RateLimit-Remaining'));
        console.log('Reset in:', response.headers.get('X-RateLimit-Reset'), 'seconds');
    });
```

---

## 🎓 EXERCISES

### Exercise 1: Get Blocked

1. Make 6 requests to `/public`
2. Watch the 6th one get blocked
3. Check `/rate-limit-status` to see your status
4. Wait 60 seconds
5. Try again - it works now!

---

### Exercise 2: Compare Tiers

**Test anonymous (no key):**
```bash
# Make 6 requests - 6th one blocked
for i in {1..6}; do curl http://localhost:8000/public; done
```

**Test with API key:**
```bash
# Make 6 requests - all succeed!
for i in {1..6}; do 
    curl http://localhost:8000/public -H "X-API-Key: test-key-123"
done
```

---

### Exercise 3: Create Your Own API Key

1. Go to http://localhost:8000/docs
2. Find `POST /get-api-key`
3. Try it with username: `yourname`
4. You get a new API key!
5. Use it in your requests

---

## 🔍 CODE WALKTHROUGH

### The Core Rate Limit Check

```python
def check_rate_limit(user, tier):
    # 1. Get their limit (5 for free, 20 for authenticated, etc.)
    limit = LIMITS[tier]
    
    # 2. Get their current count
    count = user_data["count"]
    
    # 3. Check if they exceeded
    if count >= limit:
        return False  # BLOCKED!
    
    # 4. Increment counter
    user_data["count"] += 1
    
    return True  # ALLOWED!
```

**That's literally it!** Everything else is just details.

---

## 💡 WHY THIS MATTERS

### Real-World Scenarios:

**1. Prevent DoS Attacks**
```
Hacker sends 10,000 requests/second
→ Without rate limit: Server crashes
→ With rate limit: Only 5 req/min allowed, hacker blocked
```

**2. Protect Expensive Operations**
```
Your AI API costs $0.01 per request
User makes 100,000 requests
→ Without rate limit: You pay $1,000
→ With rate limit: User limited to 50 requests (you pay $0.50)
```

**3. Fair Usage**
```
One user makes 1 million requests
Other users can't access the API
→ With rate limiting: Everyone gets fair share
```


## ✅ COMPLETION CHECKLIST

- [ ] Installed dependencies
- [ ] Server runs successfully
- [ ] Got rate limited (6 requests)
- [ ] Tested with API key
- [ ] Checked rate limit status
- [ ] Created your own API key
- [ ] Understand the 3 tiers
- [ ] Can explain how it works
- [ ] Can answer interview questions

---

## 🎯 KEY TAKEAWAYS

**3 Simple Ideas:**

1. **Count requests** - Keep track of how many requests each user makes
2. **Set limits** - Decide max requests per time period
3. **Block excess** - Return 429 error if limit exceeded

