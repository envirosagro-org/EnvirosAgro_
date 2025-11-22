#!/usr/bin/env python3
"""Check which local Streamlit ports respond with HTTP 200.

Checks localhost on ports 8501-8503 and prints a short report.
"""
from http.client import HTTPConnection


def check_port(host: str, port: int, timeout: float = 1.0) -> bool:
    conn = HTTPConnection(host, port, timeout=timeout)
    try:
        conn.request("GET", "/")
        resp = conn.getresponse()
        return resp.status == 200
    except Exception:
        return False
    finally:
        try:
            conn.close()
        except Exception:
            pass


def main() -> int:
    host = "localhost"
    ports = [8501, 8502, 8503]
    ok = []
    for p in ports:
        up = check_port(host, p)
        print(f"port {p}: {'OK' if up else 'no response'}")
        if up:
            ok.append(p)

    if ok:
        print(f"Streamlit appears up on: {', '.join(str(p) for p in ok)}")
        return 0
    print("No Streamlit instances detected on ports 8501-8503.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
