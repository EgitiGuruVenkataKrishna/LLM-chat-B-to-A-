from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total API Requests"
)

ERROR_COUNT = Counter(
    "api_errors_total",
    "Total API Errors"
)

REQUEST_TIME = Histogram(
    "api_request_duration_seconds",
    "Request latency"
)