"""Main FastAPI application."""
import logging
import uvicorn

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from starlette_exporter import PrometheusMiddleware
from prometheus_client import Counter, Histogram, push_to_gateway
from prometheus_client.core import CollectorRegistry
from utils import ConfigParameters

logging.basicConfig(filename="fastapi.log", level=logging.DEBUG)

app = FastAPI(title="Base App", description="Main FastAPI Example.")
app.add_middleware(PrometheusMiddleware)
config = ConfigParameters()

# Metrics registry
registry = CollectorRegistry()

# Counter for requests
REQUESTS = Counter(
    "http_requests_total", "Total HTTP Requests", ["method", "path"], registry=registry
)

# Histogram for response times
TIMES = Histogram(
    "http_request_duration_seconds",
    "HTTP Request Duration",
    ["method", "path"],
    registry=registry,
)


@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    """
    A middleware to monitor incoming HTTP requests.
    """
    method = request.method
    path = request.url.path

    with REQUESTS.labels(method=method, path=path).count_exceptions():
        with TIMES.labels(method=method, path=path).time():
            # Push gateway
            push_to_gateway("localhost:9091", job="FastAPI", registry=registry)

            # Logging
            logging.info(msg=f"Method: {method} | Path: {path}")

            # Call function
            response = await call_next(request)
            return response


@app.get("/error")
async def error():
    """
    Endpoint to generate a HTTP exception.
    """
    logging.error(msg="Encounter an error ..")
    raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get('/')
async def root():
    """
    Root endpoint.
    """
    return HTMLResponse(content='<html><head><title>FastAPI with Prometheus</title></head><body><h1>FastAPI with Prometheus</h1></body></html>', status_code=200)  # NOQA


if __name__ == "__main__":
    logging.info(msg="FastAPI starting...")
    uvicorn.run(
        app=app,
        host=config.get(section="server", key="host"),
        port=int(config.get(section="server", key="port")),
    )
