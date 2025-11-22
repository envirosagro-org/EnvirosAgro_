import os
import urllib.request
import pytest


def _check_ports(ports):
    for p in ports:
        url = f"http://localhost:{p}/"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "smoke-test"})
            with urllib.request.urlopen(req, timeout=2) as resp:
                if getattr(resp, "status", None) == 200:
                    return True
        except Exception:
            continue
    return False


def test_streamlit_smoke():
    """Smoke test that checks localhost:8501-8503 for a running Streamlit app.

    This test is skipped by default unless `RUN_SMOKE_TESTS=1` is set in
    the environment. That keeps CI fast and predictable while allowing
    opt-in runtime checks locally or in specialized pipelines.
    """
    if os.getenv("RUN_SMOKE_TESTS") != "1":
        pytest.skip("Skipping smoke test; set RUN_SMOKE_TESTS=1 to enable")

    ports = [8501, 8502, 8503]
    ok = _check_ports(ports)
    assert ok, "No Streamlit instance returned HTTP 200 on ports 8501-8503"
