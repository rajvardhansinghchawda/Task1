import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from handler import send_email


def _load_dotenv_file(dotenv_path: str) -> None:
    """
    Minimal .env loader (no external dependency).
    Only sets variables that are not already in the environment.
    """
    try:
        with open(dotenv_path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip("'").strip('"')
                if key and key not in os.environ:
                    os.environ[key] = value
    except FileNotFoundError:
        return


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):  # noqa: N802
        if self.path != "/send-email":
            return self._send_json(404, {"message": "Not found"})

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(content_length) if content_length > 0 else b"{}"
            # Keep the same event shape used by serverless httpApi
            event = {"body": raw.decode("utf-8")}
            result = send_email(event, context=None)
            status = int(result.get("statusCode", 500))
            body = result.get("body", "{}")
            try:
                payload = json.loads(body) if isinstance(body, str) else body
            except Exception:
                payload = {"message": body}
            return self._send_json(status, payload)
        except Exception as e:
            return self._send_json(500, {"message": "Local server error", "error": str(e)})

    def log_message(self, fmt, *args):  # silence default logging
        return


def main():
    # Load env vars from project root .env if present
    here = os.path.dirname(os.path.abspath(__file__))
    project_root_env = os.path.abspath(os.path.join(here, "..", ".env"))
    _load_dotenv_file(project_root_env)

    host = os.environ.get("EMAIL_SERVICE_HOST", "127.0.0.1")
    port = int(os.environ.get("EMAIL_SERVICE_PORT", "3000"))
    server = HTTPServer((host, port), Handler)
    print(f"Email service listening on http://{host}:{port}/send-email")
    server.serve_forever()


if __name__ == "__main__":
    main()

