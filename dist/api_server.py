import json, time, sys, os, math
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, '/home/openclaw/.openclaw/workspace/evez-os-sensors')

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self._serve_landing()
        elif path == "/api/health":
            self._json({"status": "LIVE", "version": "2.0", "ts": time.time()})
        elif path == "/api/wash-trading":
            self._wash_trading()
        elif path == "/api/status":
            self._json({"name": "TRONOVSILNILZYN", "lyapunov": 0.2948, "betti": [1,0,46], "systems": 17, "loc": 8762})
        elif path == "/api/poly-c":
            p = parse_qs(urlparse(self.path).query)
            omega = float(p.get("omega", [0.5])[0])
            topo = float(p.get("topo", [1.0])[0])
            n = int(p.get("n", [1])[0])
            val = (1.0 * omega * topo) / (2 * math.sqrt(max(n, 1)))
            self._json({"value": round(val, 6), "formula": "poly_c = tau * omega * topo / 2*sqrt(N)"})
        else:
            self._json({"error": "Not found", "endpoints": ["/", "/api/health", "/api/wash-trading", "/api/status", "/api/poly-c"]}, 404)

    def _serve_landing(self):
        try:
            with open("/home/openclaw/.openclaw/workspace/dist/index.html") as f:
                html = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def _wash_trading(self):
        import urllib.request, ssl
        ctx = ssl.create_default_context()
        try:
            req = urllib.request.Request(
                "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=volume_desc&per_page=10&page=1",
                headers={"User-Agent": "EVEZ-OS/2.0"})
            with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
                data = json.loads(r.read())
        except Exception as e:
            self._json({"status": "API_UNREACHABLE", "error": str(e)[:80]})
            return

        findings = []
        for coin in data:
            sym = coin.get("symbol", "?")
            mcap = coin.get("market_cap") or 0
            vol = coin.get("total_volume") or 0
            if mcap == 0: continue
            vm = vol / mcap
            if vm > 1.0:
                plp = min(1.0, vm/5) * 0.8 * 0.8 * 0.7 * min(1.0, vm/3)
                findings.append({"symbol": sym, "name": coin.get("name","?"),
                    "price": coin.get("current_price",0),
                    "vol_mcap": round(vm,4), "plp": round(plp,4),
                    "verdict": "INEVITABLE" if plp>0.8 else "FORMING" if plp>0.5 else "POSSIBLE"})
        self._json({"status": "LIVE", "source": "CoinGecko", "findings": findings})

    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, default=str).encode())

    def log_message(self, *a): pass

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9090
    print(f"EVEZ-OS API on :{port}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
