import argparse
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from fol.knowledge_base import KnowledgeBase
from fol.engine import Engine
from web import api

STATIC = Path(__file__).parent / "static"


class App:
    def __init__(self, kb_path):
        self.kb_path = str(kb_path)
        self.kb = KnowledgeBase.from_file(kb_path)
        self.engine = Engine(self.kb)

    def get(self, path, params):
        if path == "/api/info":
            return {"kb_path": self.kb_path, **api.kb_overview(self.kb)}
        if path == "/api/clauses":
            return {"clauses": api.clauses(self.kb, params.get("predicate", ""))}
        if path == "/api/curriculum":
            return api.curriculum(self.engine)
        if path == "/api/examples":
            return api.examples()
        return None

    def post(self, path, body):
        if path == "/api/query":
            return api.run_query(self.engine, body.get("query", ""), bool(body.get("trace")))
        return None


def make_handler(app):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            url = urlparse(self.path)
            if url.path in ("/", "/index.html"):
                return self.send_file(STATIC / "index.html", "text/html; charset=utf-8")
            params = {k: v[0] for k, v in parse_qs(url.query).items()}
            self.send_json(app.get(url.path, params))

        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            try:
                body = json.loads(self.rfile.read(length) or b"{}")
            except json.JSONDecodeError:
                return self.send_json({"ok": False, "error": "json invalid"}, 400)
            self.send_json(app.post(urlparse(self.path).path, body))

        def send_json(self, data, status=200):
            if data is None:
                data, status = {"ok": False, "error": "ruta necunoscuta"}, 404
            self.send_bytes(json.dumps(data, ensure_ascii=False).encode("utf-8"),
                            "application/json; charset=utf-8", status)

        def send_file(self, path, content_type):
            self.send_bytes(path.read_bytes(), content_type)

        def send_bytes(self, payload, content_type, status=200):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, format, *args):
            pass

    return Handler


def main(argv=None):
    parser = argparse.ArgumentParser(description="interfata web pentru motorul FOL")
    parser.add_argument("kb", nargs="?", default="kb/curriculum.kb")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args(argv)
    app = App(args.kb)
    server = HTTPServer(("127.0.0.1", args.port), make_handler(app))
    url = f"http://127.0.0.1:{args.port}"
    print(f"Am incarcat {len(app.kb)} clauze din {args.kb}.")
    print(f"Interfata web: {url}   (Ctrl+C pentru oprire)")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
