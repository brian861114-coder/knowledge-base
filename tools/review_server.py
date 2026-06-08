#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from kb_paths import repo_root


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class ReviewRequestHandler(BaseHTTPRequestHandler):
    server_version = "KnowledgeMapReview/0.1"

    def _json_response(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _text_response(self, payload: bytes, content_type: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _load_manifest(self) -> dict:
        return read_json(self.server.session_dir / "manifest.json")

    def _load_decisions(self) -> dict:
        return read_json(self.server.session_dir / "decisions.json")

    def _send_not_found(self) -> None:
        self._json_response({"error": "not_found"}, status=404)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/session":
            manifest = self._load_manifest()
            decisions = self._load_decisions()
            payload = dict(manifest)
            payload["decisions"] = decisions
            return self._json_response(payload)

        if parsed.path == "/api/decisions":
            return self._json_response(self._load_decisions())

        if parsed.path.startswith("/api/item/"):
            item_id = parsed.path.split("/")[-1]
            item_path = self.server.session_dir / "items" / f"{item_id}.json"
            if not item_path.exists():
                return self._send_not_found()
            item = read_json(item_path)
            decisions = self._load_decisions()
            item["review_decision"] = decisions.get(item_id, {"decision": "pending", "updated_at": None})
            return self._json_response(item)

        return self._serve_static(parsed.path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/decision":
            return self._send_not_found()

        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length)
        payload = json.loads(raw_body.decode("utf-8"))

        item_id = str(payload.get("item_id", "")).strip()
        decision = str(payload.get("decision", "")).strip()
        if not item_id or decision not in {"approved", "rejected", "skipped", "pending"}:
            return self._json_response({"error": "invalid_payload"}, status=400)

        decisions = self._load_decisions()
        if item_id not in decisions:
            return self._send_not_found()

        decisions[item_id] = {
            "decision": decision,
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }
        write_json(self.server.session_dir / "decisions.json", decisions)
        return self._json_response({"ok": True, "item_id": item_id, "decision": decision})

    def log_message(self, format: str, *args) -> None:
        return

    def _serve_static(self, request_path: str) -> None:
        static_root = self.server.static_root
        relative = request_path.lstrip("/") or "index.html"
        target = (static_root / relative).resolve()
        if not str(target).startswith(str(static_root.resolve())) or not target.exists() or target.is_dir():
            target = static_root / "index.html"

        content_type = {
            ".html": "text/html; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".css": "text/css; charset=utf-8",
        }.get(target.suffix, "application/octet-stream")
        self._text_response(target.read_bytes(), content_type)


class ReviewHTTPServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], session_dir: Path, static_root: Path):
        super().__init__(server_address, ReviewRequestHandler)
        self.session_dir = session_dir
        self.static_root = static_root


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve the local review UI for a prepared review session.")
    parser.add_argument("--session-dir", required=True, help="Path to tmp/review_sessions/<session-id>.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    session_dir = Path(args.session_dir).resolve()
    static_root = (repo_root() / "review_app").resolve()
    if not (session_dir / "manifest.json").exists():
        raise SystemExit(f"Session manifest not found: {session_dir}")
    if not static_root.exists():
        raise SystemExit(f"Static review app not found: {static_root}")

    server = ReviewHTTPServer((args.host, args.port), session_dir, static_root)
    print(f"Serving review session at http://{args.host}:{args.port}")
    print(f"Session dir: {session_dir}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
