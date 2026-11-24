"""Single-user Railway gateway. Fail closed if no strong password configured."""
import base64
import binascii
import hmac
import os

class AuthGate:
    def __init__(self, app, username, password):
        self.app = app
        self.expected = (username + ":" + password).encode("utf-8")
        self.ready = bool(username) and ":" not in username and len(password) >= 16

    async def __call__(self, scope, receive, send):
        kind = scope["type"]
        if kind == "lifespan":
            return await self.app(scope, receive, send)
        if kind == "websocket":
            return await send({"type": "websocket.close", "code": 1008})
        if kind != "http":
            return
        async def reply(status, body, headers=()):
            await send({"type": "http.response.start", "status": status, "headers": [(b"content-type", b"text/plain"), (b"cache-control", b"no-store"), *headers]})
            await send({"type": "http.response.body", "body": body})
        if scope["path"] == "/healthz" and scope["method"] in ("GET", "HEAD"):
            return await reply(200, b"ok")
        if not self.ready:
            return await reply(503, b"Configure APP_PASSWORD (at least 16 characters) in Railway.")
        headers = dict(scope.get("headers", []))
        scheme, _, token = headers.get(b"authorization", b"").partition(b" ")
        try:
            supplied = base64.b64decode(token, validate=True) if scheme.lower() == b"basic" else b""
        except (ValueError, binascii.Error):
            supplied = b""
        if not hmac.compare_digest(supplied, self.expected):
            return await reply(401, b"Authentication required", [(b"www-authenticate", b'Basic realm="LDraw Nova", charset="UTF-8"')])
        if headers.get(b"sec-fetch-site") == b"cross-site":
            return await reply(403, b"Cross-site requests are not allowed")
        # Do not pass the gateway credential to upstream request handlers.
        scope = dict(scope)
        scope["headers"] = [(k, v) for k, v in scope.get("headers", []) if k != b"authorization"]
        return await self.app(scope, receive, send)

# Read authentication credentials before upstream settings initialize.
_username = os.environ.get("APP_USERNAME", "admin")
_password = os.environ.get("APP_PASSWORD", "")
from main import app as upstream_app
app = AuthGate(upstream_app, _username, _password)
