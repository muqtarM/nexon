from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response

REQUEST_COUNT = Counter(
    "nexon_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"]
)
REQUEST_LATENCY = Histogram(
    "nexon_http_request_duration_seconds",
    "Request latency",
    ["method", "path"]
)


def setup_metrics(app):
    @app.middleware("http")
    async def prometheus_middleware(request: Request, call_next):
        start = request.state.start_time = (request.scope.get("start_time")
                                            or request.scope.setdefault("start_time", __import__("time").time()))
        response = await call_next(request)
        latency = __import__("time").time() - start
        REQUEST_LATENCY.labels(request.method, request.url.path).observe(latency)
        REQUEST_COUNT.labels(request.method, request.url.path, response.status_code).inc()
        return response

    @app.get("/metrics")
    def metrics_endpoint():
        data = generate_latest()
        return Response(data, media_type=CONTENT_TYPE_LATEST)
