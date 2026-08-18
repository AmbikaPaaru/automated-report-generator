"""Regression test: CORS headers must survive an unhandled exception.

Starlette's CORSMiddleware doesn't see responses from exceptions that propagate
past it. A plain @app.exception_handler(Exception) doesn't fix this either --
Starlette attaches bare-Exception handlers to the outermost ServerErrorMiddleware,
which sits *outside* CORSMiddleware. The fix in app/main.py is a BaseHTTPMiddleware
added before CORSMiddleware (so it sits inside it); this test exercises that by
adding a route that always raises, then checking the resulting 500 still carries
Access-Control-Allow-Origin for an allowed origin.
"""

from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


@app.get("/__boom__")
def _boom() -> None:
    raise RuntimeError("simulated unhandled failure")


def test_unhandled_exception_still_gets_cors_header():
    with TestClient(app) as client:
        response = client.get("/__boom__", headers={"Origin": settings.frontend_origin})

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error."}
    assert response.headers.get("access-control-allow-origin") == settings.frontend_origin


def test_disallowed_origin_does_not_get_cors_header():
    with TestClient(app) as client:
        response = client.get("/__boom__", headers={"Origin": "http://evil.example.com"})

    assert response.status_code == 500
    assert "access-control-allow-origin" not in response.headers
