#!/usr/bin/env python3
"""Serve the self-contained wireframe without third-party dependencies."""

from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WIREFRAME = ROOT / "WIREFRAME"


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve WIREFRAME/index.html locally")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=4173, type=int)
    args = parser.parse_args()

    handler = partial(SimpleHTTPRequestHandler, directory=str(WIREFRAME))
    server = ThreadingHTTPServer((args.host, args.port), handler)
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
