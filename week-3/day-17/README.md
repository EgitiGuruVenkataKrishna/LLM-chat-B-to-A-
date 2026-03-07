
# Advanced Logging & Monitoring Mini-Project

A production-style **FastAPI project** demonstrating structured logging, metrics collection, health checks, distributed tracing, and load testing. This setup mimics how modern backend/AI APIs are observed and monitored in industry-grade systems.

---

## Features

- **Structured JSON Logging**  
  Logs include request IDs, endpoints, latency, tokens used, status, and errors. Designed for machine parsing and human readability.

- **Request Correlation IDs**  
  Each request is assigned a unique ID to trace requests across asynchronous or distributed systems.

- **Prometheus Metrics Endpoint (`/metrics`)**  
  - Counters: Total requests and errors  
  - Gauges: Current active requests  
  - Histograms: Request duration distribution  
  Compatible with **Prometheus** and **Grafana** dashboards.

- **Health Check Endpoint (`/health`)**  
  Checks API status and optionally validates dependencies like database or cache connections.

- **Load Testing Support**  
  Includes a sample Python script to simulate **100+ requests** to test logging, metrics, and system stability.

- **Distributed Tracing Support (OpenTelemetry)**  
  Captures request traces across multiple services and integrates with logs and metrics for end-to-end observability.

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/EgitiGuruVenkataKrishna/LLM-chat-B-to-A-.git
cd week-3
cd day-17
````

2. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

### Run the API

```bash
uvicorn main:app --reload
```

* **/generate** → Sample API endpoint
* **/health** → Health check endpoint
* **/metrics** → Prometheus metrics

### Load Testing

```bash
python load_test.py
```

Simulates 100 requests to `/generate` and prints HTTP status codes.

### Observability

* **Structured Logs:** Streamed to console or log collector (ELK/Loki)
* **Prometheus:** Scrape `/metrics`
* **Grafana:** Visualize request rate, latency, errors
* **OpenTelemetry/Distributed Tracing:** Trace individual requests across components

---

## Metrics Overview

| Metric Name                    | Type      | Description                  |
| ------------------------------ | --------- | ---------------------------- |
| `api_requests_total`           | Counter   | Total number of requests     |
| `api_errors_total`             | Counter   | Total number of errors       |
| `api_request_duration_seconds` | Histogram | Request latency distribution |
| `active_requests`              | Gauge     | Current active requests      |

---

## Logging Structure Example

```json
{
  "timestamp": "2026-03-07T11:45:00Z",
  "level": "INFO",
  "request_id": "9a1b2c3d-4e5f-6g7h-8i9j",
  "endpoint": "/generate",
  "status": "success",
  "latency_ms": 123,
  "tokens_used": 50
}
```

---

## Best Practices Demonstrated

* Never log sensitive data (passwords, API keys, JWTs).
* Avoid high-cardinality labels in metrics (e.g., user IDs in counters).
* Include request IDs for correlation between logs, metrics, and traces.
* Use health checks beyond “alive” to include resource and dependency status.
* Use structured logging for machine-parsable and human-readable logs.

---


## References

* [Prometheus Metrics Best Practices](https://betterstack.com/community/guides/monitoring/prometheus-best-practices/?utm_source=chatgpt.com)
* [OpenTelemetry Python Docs](https://opentelemetry.io/docs/instrumentation/python/)
* [FastAPI Logging and Monitoring Guide](https://fastapi.tiangolo.com/advanced/logging/)
* [Google SRE Golden Signals](https://landing.google.com/sre/sre-book/chapters/monitoring-distributed-systems/)

---

## Author

**Krishna** – CSE AIML student passionate about AI, backend observability, and production-grade systems.




