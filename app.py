import time
from flask import Flask, g, request, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from routes.inventory_routes import inventory_bp
from routes.events_routes import events_bp
from routes.stats_routes import stats_bp

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "http_status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency, in seconds",
    ["endpoint"],
)


def create_app():
    app = Flask(__name__)
    app.register_blueprint(inventory_bp, url_prefix="/api/inventory")
    app.register_blueprint(events_bp, url_prefix="/api/events")
    app.register_blueprint(stats_bp, url_prefix="/api/stats")

    @app.before_request
    def start_timer():
        g.start_time = time.time()

    @app.after_request
    def record_metrics(response):
        endpoint = request.endpoint or "unknown"
        start_time = getattr(g, "start_time", None)
        if start_time is not None:
            latency = time.time() - start_time
            REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            http_status=response.status_code,
        ).inc()
        return response

    @app.get("/metrics")
    def metrics():
        data = generate_latest()
        return Response(data, mimetype=CONTENT_TYPE_LATEST)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
