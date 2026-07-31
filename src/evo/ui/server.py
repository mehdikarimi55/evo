"""Stdlib localhost UI for EVO Terrarium."""

from __future__ import annotations

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse
import json
import webbrowser

from evo.autonomy import AutonomyController, AutonomyError
from evo.config import ConfigurationError
from evo.kernel.budget import BudgetExceeded
from evo.providers.groq import ProviderError
from evo.runtime import TerrariumRuntime, serialize_error

STATIC_DIR = Path(__file__).resolve().parent / "static"
INDEX_FILE = STATIC_DIR / "index.html"


class TerrariumUIServer(ThreadingHTTPServer):
    def __init__(
        self,
        server_address: tuple[str, int],
        runtime: TerrariumRuntime,
    ) -> None:
        self.runtime = runtime
        self.autonomy = AutonomyController(
            evolve=runtime.evolve,
            state_path=runtime.workspace / ".evo/autonomy-state.json",
            journal_path=runtime.workspace / ".evo/evolution-journal.jsonl",
        )
        super().__init__(server_address, TerrariumRequestHandler)

    def server_close(self) -> None:
        self.autonomy.shutdown()
        super().server_close()


class TerrariumRequestHandler(BaseHTTPRequestHandler):
    server: TerrariumUIServer

    def log_message(self, format: str, *args: object) -> None:
        return

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/index.html"}:
            self._send_file(INDEX_FILE, "text/html; charset=utf-8")
            return
        if parsed.path == "/api/settings":
            self._send_json(self.server.runtime.public_settings())
            return
        if parsed.path == "/api/doctor":
            self._run_json(lambda: self.server.runtime.doctor())
            return
        if parsed.path == "/api/audit":
            query = parse_qs(parsed.query)
            limit = int(query.get("limit", ["50"])[0])
            search = query.get("q", [""])[0]
            self._run_json(
                lambda: {
                    "events": self.server.runtime.read_audit(
                        limit=limit, query=search
                    )
                }
            )
            return
        if parsed.path == "/api/autonomy":
            self._send_json(self.server.autonomy.status())
            return
        if parsed.path == "/api/evolution-journal":
            query = parse_qs(parsed.query)
            limit = int(query.get("limit", ["100"])[0])
            self._run_json(
                lambda: {
                    "entries": self.server.autonomy.read_journal(limit=limit)
                }
            )
            return
        if parsed.path.startswith("/static/"):
            relative = parsed.path.removeprefix("/static/")
            target = (STATIC_DIR / relative).resolve()
            if not str(target).startswith(str(STATIC_DIR)) or not target.is_file():
                self._send_json(
                    {"error": "Static asset not found."},
                    status=HTTPStatus.NOT_FOUND,
                )
                return
            content_type = (
                "text/css; charset=utf-8"
                if target.suffix == ".css"
                else "application/javascript; charset=utf-8"
                if target.suffix == ".js"
                else "application/octet-stream"
            )
            self._send_file(target, content_type)
            return
        self._send_json({"error": "API endpoint not found."}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            body = self._read_json_body()
        except (ValueError, json.JSONDecodeError) as exc:
            self._send_json(serialize_error(exc), status=HTTPStatus.BAD_REQUEST)
            return
        if parsed.path == "/api/settings":
            self._run_json(lambda: self.server.runtime.save_settings(body))
            return
        if parsed.path == "/api/probe":
            self._run_json(lambda: {"message": self.server.runtime.probe()})
            return
        if parsed.path == "/api/evolve":
            mutable_paths = body.get("mutable_paths") or ["organisms/"]
            if isinstance(mutable_paths, str):
                mutable_paths = [
                    part.strip() for part in mutable_paths.split(",") if part.strip()
                ]
            self._run_json(
                lambda: self.server.runtime.evolve(
                    task=str(body.get("task", "")),
                    mutable_paths=list(mutable_paths),
                    language=str(body.get("language", "en")),
                )
            )
            return
        if parsed.path == "/api/autonomy/start":
            self._run_json(lambda: self.server.autonomy.start(body))
            return
        if parsed.path == "/api/autonomy/stop":
            self._run_json(lambda: self.server.autonomy.stop())
            return
        self._send_json({"error": "API endpoint not found."}, status=HTTPStatus.NOT_FOUND)

    def _read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        if not raw:
            return {}
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("بدنه JSON باید یک شیء باشد")
        return payload

    def _run_json(self, action: Any) -> None:
        try:
            payload = action()
        except (
            ConfigurationError,
            AutonomyError,
            ProviderError,
            BudgetExceeded,
            ValueError,
            json.JSONDecodeError,
        ) as exc:
            self._send_json(serialize_error(exc), status=HTTPStatus.BAD_REQUEST)
        except Exception as exc:
            self._send_json(
                serialize_error(exc),
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        else:
            self._send_json(payload)

    def _send_json(
        self, payload: dict[str, Any] | list[Any], status: HTTPStatus = HTTPStatus.OK
    ) -> None:
        body = json.dumps(payload, default=str, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path, content_type: str) -> None:
        body = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def serve_ui(
    *,
    runtime: TerrariumRuntime,
    host: str = "127.0.0.1",
    port: int = 8787,
    open_browser: bool = True,
) -> None:
    if host not in {"127.0.0.1", "localhost"}:
        raise ValueError("رابط کاربری فقط می‌تواند روی localhost اجرا شود")
    server = TerrariumUIServer((host, port), runtime)
    url = f"http://{host}:{port}/"
    print(f"رابط کاربری EVO در این نشانی آماده است: {url}", flush=True)
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nرابط کاربری EVO متوقف شد.")
    finally:
        server.server_close()
