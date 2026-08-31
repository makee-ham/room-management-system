#!/usr/bin/env python3
"""Serve the wireframe and its public, browser-safe runtime configuration."""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import os
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
WIREFRAME = ROOT / "WIREFRAME"
ENV_FILE = ROOT / ".env.local"
RUNTIME_CONFIG_PATH = "/runtime-config.json"
RUNTIME_MODE_ENV_NAME = "RMS_RUNTIME_MODE"
DOCUMENTED_PROJECT_REF = "aodikrxcczbogjpsjwjt"
RUNTIME_ENV_NAMES = {
    "apiBaseUrl": "RMS_API_BASE_URL",
    "supabaseUrl": "SUPABASE_URL",
    "supabasePublishableKey": "SUPABASE_PUBLISHABLE_KEY",
    "sessionPersistence": "RMS_SESSION_PERSISTENCE",
}
ERROR_RUNTIME_CONFIG = {
    "mode": "error",
    "apiBaseUrl": "",
    "supabaseUrl": "",
    "supabasePublishableKey": "",
    "sessionPersistence": "session",
}
DEMO_RUNTIME_CONFIG = {**ERROR_RUNTIME_CONFIG, "mode": "demo"}


def parse_env_file(path: Path) -> dict[str, str]:
    """Read the small dotenv subset used by local public runtime settings."""
    if not path.is_file():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        else:
            value = re.split(r"\s+#", value, maxsplit=1)[0].rstrip()
        values[name] = value
    return values


def project_ref_from_url(value: str, expected_path: str) -> str | None:
    try:
        parsed = urlparse(value)
        hostname = parsed.hostname or ""
        port = parsed.port
    except (TypeError, ValueError):
        return None

    normalized_path = parsed.path.rstrip("/")
    if (
        parsed.scheme.lower() != "https"
        or parsed.username is not None
        or parsed.password is not None
        or port is not None
        or parsed.query
        or parsed.fragment
        or normalized_path != expected_path.rstrip("/")
    ):
        return None
    match = re.fullmatch(r"([a-z0-9]+)\.supabase\.co", hostname.lower())
    return match.group(1) if match else None


def is_browser_publishable_key(value: str) -> bool:
    """Accept current opaque publishable keys and legacy browser anon JWTs."""
    if re.fullmatch(r"sb_publishable_[A-Za-z0-9_-]{20,}", value):
        return True
    if not re.fullmatch(
        r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", value
    ):
        return False

    try:
        payload_segment = value.split(".", 2)[1]
        padding = "=" * (-len(payload_segment) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_segment + padding))
    except (binascii.Error, UnicodeDecodeError, ValueError, json.JSONDecodeError):
        return False
    return isinstance(payload, dict) and payload.get("role") == "anon"


def load_runtime_config() -> dict[str, str]:
    file_values = parse_env_file(ENV_FILE)
    requested_mode = os.environ.get(
        RUNTIME_MODE_ENV_NAME, file_values.get(RUNTIME_MODE_ENV_NAME, "")
    ).strip().lower()
    if requested_mode == "demo":
        return DEMO_RUNTIME_CONFIG.copy()
    if requested_mode not in {"", "live"}:
        return ERROR_RUNTIME_CONFIG.copy()

    values = {
        output_name: os.environ.get(env_name, file_values.get(env_name, "")).strip()
        for output_name, env_name in RUNTIME_ENV_NAMES.items()
    }

    refs = (
        project_ref_from_url(values["apiBaseUrl"], "/functions/v1/api"),
        project_ref_from_url(values["supabaseUrl"], ""),
    )
    persistence = values["sessionPersistence"].lower()
    if (
        not all(refs)
        or len(set(refs)) != 1
        or refs[0] != DOCUMENTED_PROJECT_REF
        or not is_browser_publishable_key(values["supabasePublishableKey"])
        or persistence not in {"local", "session"}
    ):
        return ERROR_RUNTIME_CONFIG.copy()

    return {
        "mode": "live",
        "apiBaseUrl": values["apiBaseUrl"].rstrip("/"),
        "supabaseUrl": values["supabaseUrl"].rstrip("/"),
        "supabasePublishableKey": values["supabasePublishableKey"],
        "sessionPersistence": persistence,
    }


class RuntimeConfigHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, directory=str(WIREFRAME), **kwargs)

    def end_headers(self) -> None:
        path = urlparse(self.path).path
        if path in {"/", "/index.html", "/sw.js", "/app.webmanifest"}:
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Pragma", "no-cache")
        super().end_headers()

    def do_GET(self) -> None:
        if urlparse(self.path).path != RUNTIME_CONFIG_PATH:
            super().do_GET()
            return

        body = json.dumps(load_runtime_config(), separators=(",", ":")).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Pragma", "no-cache")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve WIREFRAME/index.html locally")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=4173, type=int)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), RuntimeConfigHandler)
    url = f"http://{args.host}:{args.port}/index.html"
    print(f"CASTLE THE ART wireframe: {url}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
