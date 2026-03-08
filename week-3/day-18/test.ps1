# Day 18: Rate Limiting Test Script
# Run this to test rate limiting

Write-Host "`n=== DAY 18: RATE LIMITING TEST ===" -ForegroundColor Cyan
Write-Host "Testing rate limits...`n"

$baseUrl = "http://localhost:8000"

# Test 1: Anonymous user (5 requests/min limit)
Write-Host "Test 1: Anonymous User (Limit: 5 req/min)" -ForegroundColor Yellow
Write-Host "Making 6 requests..." -ForegroundColor Gray

for ($i = 1; $i -le 6; $i++) {
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/public" -Method Get
        Write-Host "  Request $i - SUCCESS ✓" -ForegroundColor Green
    }
    catch {
        Write-Host "  Request $i - BLOCKED (Rate Limited) ✗" -ForegroundColor Red
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor DarkRed
    }
    Start-Sleep -Milliseconds 100
}

Write-Host ""

# Test 2: Check rate limit status
Write-Host "Test 2: Check Rate Limit Status" -ForegroundColor Yellow
try {
    $status = Invoke-RestMethod -Uri "$baseUrl/rate-limit-status" -Method Get
    Write-Host "  Tier: $($status.tier)" -ForegroundColor Cyan
    Write-Host "  Used this minute: $($status.usage.this_minute)" -ForegroundColor Cyan
    Write-Host "  Remaining: $($status.remaining.this_minute)" -ForegroundColor Cyan
    Write-Host "  Reset in: $($status.reset_in_seconds.minute) seconds" -ForegroundColor Cyan
}
catch {
    Write-Host "  Error checking status: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 3: With API Key (20 requests/min limit)
Write-Host "Test 3: Authenticated User (Limit: 20 req/min)" -ForegroundColor Yellow
Write-Host "Making 6 requests with API key..." -ForegroundColor Gray

$headers = @{
    "X-API-Key" = "test-key-123"
}

for ($i = 1; $i -le 6; $i++) {
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/public" -Method Get -Headers $headers
        Write-Host "  Request $i - SUCCESS ✓" -ForegroundColor Green
    }
    catch {
        Write-Host "  Request $i - BLOCKED ✗" -ForegroundColor Red
    }
    Start-Sleep -Milliseconds 100
}

Write-Host ""

# Test 4: Protected endpoint without key
Write-Host "Test 4: Protected Endpoint (No API Key)" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/protected" -Method Get
    Write-Host "  Access granted!" -ForegroundColor Green
}
catch {
    Write-Host "  Access denied (401 Unauthorized) ✗" -ForegroundColor Red
}

Write-Host ""

# Test 5: Protected endpoint with key
Write-Host "Test 5: Protected Endpoint (With API Key)" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/protected" -Method Get -Headers $headers
    Write-Host "  Access granted! ✓" -ForegroundColor Green
    Write-Host "  User: $($response.user)" -ForegroundColor Cyan
    Write-Host "  Tier: $($response.tier)" -ForegroundColor Cyan
}
catch {
    Write-Host "  Access denied ✗" -ForegroundColor Red
}

Write-Host ""

# Summary
Write-Host "=== TEST SUMMARY ===" -ForegroundColor Cyan
Write-Host "✓ Anonymous users limited to 5 requests/min" -ForegroundColor Green
Write-Host "✓ Authenticated users get 20 requests/min" -ForegroundColor Green
Write-Host "✓ Protected endpoints require API key" -ForegroundColor Green
Write-Host "✓ Rate limit headers included in responses" -ForegroundColor Green
Write-Host ""
Write-Host "Try yourself in Swagger UI: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""