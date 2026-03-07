# Day 17: Test Script
# Run this after starting the server to test all endpoints

Write-Host "`n=== DAY 17: LOGGING DEMO - TEST SCRIPT ===" -ForegroundColor Cyan
Write-Host "Make sure the server is running (python main.py)`n"

$baseUrl = "http://localhost:8000"

# Test 1: Health Check
Write-Host "Test 1: Health Check" -ForegroundColor Green
$response = Invoke-RestMethod -Uri "$baseUrl/" -Method Get
Write-Host "Response: $($response | ConvertTo-Json -Compress)"
Write-Host ""

Start-Sleep -Seconds 1

# Test 2: Process Data (Normal Priority)
Write-Host "Test 2: Process Data (Normal)" -ForegroundColor Green
$body = @{
    data = "Hello, this is test data"
    priority = "normal"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "$baseUrl/process" -Method Post -Body $body -ContentType "application/json"
Write-Host "Response: $($response | ConvertTo-Json -Compress)"
Write-Host ""

Start-Sleep -Seconds 1

# Test 3: Process Data (High Priority)
Write-Host "Test 3: Process Data (High Priority - Faster)" -ForegroundColor Green
$body = @{
    data = "High priority processing"
    priority = "high"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "$baseUrl/process" -Method Post -Body $body -ContentType "application/json"
Write-Host "Response: $($response | ConvertTo-Json -Compress)"
Write-Host ""

Start-Sleep -Seconds 1

# Test 4: Create User
Write-Host "Test 4: Create User" -ForegroundColor Green
$body = @{
    name = "John Doe"
    email = "john@example.com"
    age = 30
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "$baseUrl/user" -Method Post -Body $body -ContentType "application/json"
Write-Host "Response: $($response | ConvertTo-Json -Compress)"
Write-Host ""

Start-Sleep -Seconds 1

# Test 5: Slow Endpoint (will trigger slow request warning)
Write-Host "Test 5: Slow Endpoint (2 seconds - will show warning in logs)" -ForegroundColor Yellow
$response = Invoke-RestMethod -Uri "$baseUrl/slow?delay_ms=2000" -Method Get
Write-Host "Response: $($response | ConvertTo-Json -Compress)"
Write-Host ""

Start-Sleep -Seconds 1

# Test 6: Error Endpoint (validation error)
Write-Host "Test 6: Error Endpoint (Validation)" -ForegroundColor Red
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/error?error_type=validation" -Method Get
} catch {
    Write-Host "Expected error: $($_.Exception.Message)"
}
Write-Host ""

Start-Sleep -Seconds 1

# Test 7: Analytics
Write-Host "Test 7: Analytics" -ForegroundColor Green
$response = Invoke-RestMethod -Uri "$baseUrl/analytics" -Method Get
Write-Host "Response: $($response | ConvertTo-Json)"
Write-Host ""

Start-Sleep -Seconds 1

# Test 8: Recent Logs
Write-Host "Test 8: Recent Logs (Last 5)" -ForegroundColor Green
$response = Invoke-RestMethod -Uri "$baseUrl/logs/recent?count=5" -Method Get
Write-Host "Found $($response.count) recent logs"
Write-Host ""

# Summary
Write-Host "`n=== TEST SUMMARY ===" -ForegroundColor Cyan
Write-Host "All tests completed!"
Write-Host ""
Write-Host "Check your logs:" -ForegroundColor Yellow
Write-Host "  - logs/app.log (all logs)"
Write-Host "  - logs/error.log (errors only)"
Write-Host ""
Write-Host "View logs:" -ForegroundColor Yellow
Write-Host "  Get-Content logs\app.log -Tail 20"
Write-Host "  Get-Content logs\error.log"
Write-Host ""
Write-Host "Next: Try the exercises in README.md!" -ForegroundColor Green