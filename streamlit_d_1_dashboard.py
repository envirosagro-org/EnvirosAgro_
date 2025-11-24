"""
EnvirosAgro Streamlit Dashboard (D1-enabled)

This single-file Streamlit app connects to the Cloudflare Worker / D1 API to: 
- fetch county list and sustainability summaries
- run on-the-fly C(a) and m calculations for scenario testing
- upload local agriculture CSVs for preview (does not auto-ingest into D1 unless you call an ingestion endpoint)
- run simple 10-year adoption & m(t) simulations and plot results

USAGE
1. Install dependencies:
   pip install streamlit pandas requests matplotlib numpy

2. Set environment variable:
   export ENVIROS_AGRO_API="https://your-worker-subdomain.workers.dev"   # replace with your worker URL

3. Run locally:
   streamlit run streamlit_d1_dashboard.py

NOTES
- This app assumes your Cloudflare Worker exposes the following endpoints:
  GET /counties            -> returns list of counties (JSON array)
  GET /summary/{county}    -> returns sustainability summary for a county
  POST /ingest/agriculture -> (optional) accepts CSV payload to insert agriculture_data
  POST /compute/sync       -> (optional) trigger server-side recompute

- If your Worker uses different routes, update API paths in the API section below.

AUTH
- If your Worker requires authentication (API key), set the env var ENVIROS_API_KEY and the app will send it as an Authorization header.

"""

import os
import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO

# ------------------
# Configuration
# ------------------
API_BASE = os.environ.get('ENVIROS_AGRO_API', 'https://example-worker.workers.dev')
API_KEY = os.environ.get('ENVIROS_API_KEY', None)
HEADERS = {'Authorization': f'Bearer {API_KEY}'} if API_KEY else {}

# ------------------
# Helper functions
# ------------------
@st.cache_data(ttl=300)
def fetch_counties():
    try:
        resp = requests.get(f"{API_BASE}/counties", headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return pd.DataFrame(resp.json())
    except Exception as e:
        st.error(f"Failed to fetch counties: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_county_summary(county_name):
    try:
        url = f"{API_BASE}/summary/{requests.utils.quote(county_name)}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.warning(f"Could not fetch summary for {county_name}: {e}")
        return None

def compute_Ca_geometric(x, r, n):
    if abs(r - 1.0) < 1e-9:
        return n * x + 1.0
    return (x * (r**n - 1.0)) / (r - 1.0) + 1.0

def compute_m(Dn, f, C_a, S=12.0):
    In = f * Dn
    return float(((Dn * In * C_a) / S)**0.5)

# ------------------
# UI Layout
# ------------------
st.set_page_config(page_title="EnvirosAgro Dashboard", layout="wide")
st.title("EnvirosAgro — D1 Streamlit Dashboard")

left, right = st.columns([2,3])

with left:
    st.header("County Explorer")
    df_counties = fetch_counties()
    if df_counties.empty:
        st.info("No counties loaded from API. You can still run local simulations below.")
    else:
        st.write(f"{len(df_counties)} counties loaded from API")
        selected = st.selectbox("Choose a county", options=df_counties['county_name'].tolist())
        if selected:
            summary = fetch_county_summary(selected)
            if summary:
                st.subheader(f"Summary — {selected}")
                st.json(summary)

    st.markdown("---")
    st.header("Upload Agriculture CSV (Preview)")
    uploaded = st.file_uploader("Upload agriculture.csv", type=['csv'])
    if uploaded is not None:
        raw = uploaded.read().decode('utf-8')
        csv_df = pd.read_csv(StringIO(raw))
        st.write(csv_df.head())
        if st.button("Preview Ingest -> send to D1 (worker ingestion endpoint)"):
            try:
                resp = requests.post(f"{API_BASE}/ingest/agriculture", data=raw, headers={**HEADERS, 'Content-Type':'text/csv'})
                resp.raise_for_status()
                st.success("Ingested into D1 via worker endpoint")
            except Exception as e:
                st.error(f"Ingest failed: {e}")

with right:
    st.header("Quick Scenario Simulator")
    col1, col2 = st.columns(2)
    with col1:
        Dn = st.number_input("Effective rainfall months (Dn)", min_value=0.0, max_value=12.0, value=8.0)
        f = st.number_input("Soil retention fraction (f)", min_value=0.0, max_value=1.0, value=0.4)
        S = st.number_input("Crop moisture requirement (S months)", min_value=1.0, max_value=24.0, value=12.0)
    with col2:
        x0 = st.number_input("Initial maturity x0", min_value=0.1, value=2.0)
        r = st.number_input("Adoption growth r", min_value=0.0, value=1.08)
        n_years = st.number_input("n (years for geometric)", min_value=1, value=4)

    if st.button("Compute C(a) and m"):
        C_a = compute_Ca_geometric(x0, r, int(n_years))
        m_val = compute_m(Dn, f, C_a, S)
        st.metric("C(a)", f"{C_a:.4f}")
        st.metric("m", f"{m_val:.4f}")

    st.markdown("---")
    st.subheader("10-year Adoption & m(t) Projection")
    years = st.slider("years", 5, 20, 10)
    if st.button("Run Projection"):
        x_t = [x0 * (r**t) for t in range(years+1)]
        C_t = [compute_Ca_geometric(x, r, int(n_years)) for x in x_t]
        m_t = [compute_m(Dn, f, C, S) for C in C_t]
        proj_df = pd.DataFrame({'year': list(range(years+1)), 'x': x_t, 'C_a': C_t, 'm': m_t})
        st.line_chart(proj_df.set_index('year')[['C_a','m']])
        st.write(proj_df)

st.sidebar.header("Utilities")
if st.sidebar.button("Trigger server-side recompute (sync)"):
    try:
        resp = requests.post(f"{API_BASE}/sync", headers=HEADERS)
        resp.raise_for_status()
        st.sidebar.success("Server-side sync triggered")
    except Exception as e:
        st.sidebar.error(f"Sync failed: {e}")

st.sidebar.markdown("---")
st.sidebar.markdown("### Notes & Next Steps")
st.sidebar.write("• Update API_BASE to your worker URL; ensure CORS or auth is configured.")
st.sidebar.write("• Add map visualization by returning county geometry from the worker or hosting a GeoJSON endpoint.")
st.sidebar.write("• For production, deploy Streamlit Sharing, Render, or Railway and set env variables securely.")

# EOF
