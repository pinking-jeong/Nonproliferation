"""Streamlit MVP UI — connects to OS-PM FastAPI backend."""
import json
import os
from pathlib import Path

import httpx
import streamlit as st

API = os.getenv("OSPM_API", "http://localhost:8000")

st.set_page_config(page_title="OS-PM Demo", layout="wide")
st.title("OS-PM — Open-Source Physical Model (academic prototype)")
st.caption("VLM-based IAEA-PM-inspired analysis. Research use only — not for operational decisions.")

with st.sidebar:
    st.header("Backend")
    st.code(API)
    if st.button("Health check"):
        try:
            r = httpx.get(f"{API}/health", timeout=10)
            st.success(r.json())
        except Exception as e:  # noqa: BLE001
            st.error(str(e))

tabs = st.tabs(["1. Image", "2. Literature", "3. Fusion"])

with tabs[0]:
    st.subheader("Image Understanding")
    img = st.file_uploader("Satellite tile (PNG/JPG)", type=["png", "jpg", "jpeg"])
    geo_lat = st.number_input("Latitude", value=33.7244, format="%.6f")
    geo_lon = st.number_input("Longitude", value=51.7264, format="%.6f")
    if st.button("Analyze image", disabled=img is None):
        tmp = Path("/tmp/ospm_upload" + Path(img.name).suffix)
        tmp.write_bytes(img.getvalue())
        with st.spinner("Calling VLM..."):
            r = httpx.post(
                f"{API}/analyze/image",
                json={"image_path": str(tmp), "geo_context": {"lat": geo_lat, "lon": geo_lon}},
                timeout=120,
            )
        if r.status_code == 200:
            st.json(r.json())
        else:
            st.error(r.text)

with tabs[1]:
    st.subheader("Literature Mining (OpenAlex)")
    cc = st.text_input("Country code", value="IR")
    y0 = st.number_input("Year start", value=2018)
    y1 = st.number_input("Year end", value=2024)
    n = st.number_input("Max papers", value=10, min_value=1, max_value=100)
    if st.button("Mine literature"):
        with st.spinner("Querying OpenAlex + classifying via VLM..."):
            r = httpx.post(
                f"{API}/analyze/literature",
                json={"country_code": cc, "year_start": y0, "year_end": y1, "max_papers": n},
                timeout=600,
            )
        if r.status_code == 200:
            st.json(r.json())
            st.session_state["last_lit_indicators"] = r.json()
        else:
            st.error(r.text)

with tabs[2]:
    st.subheader("Bayesian Fusion")
    pasted = st.text_area(
        "Indicators JSON (or use last literature result)",
        value=json.dumps(st.session_state.get("last_lit_indicators", []), indent=2)[:5000],
        height=300,
    )
    prior = st.slider("Prior", 0.001, 0.5, 0.05, 0.005)
    if st.button("Fuse"):
        try:
            inds = json.loads(pasted) if pasted.strip() else []
        except json.JSONDecodeError as e:
            st.error(f"Bad JSON: {e}")
            inds = None
        if inds is not None:
            r = httpx.post(f"{API}/fuse", json={"indicators": inds, "prior": prior}, timeout=60)
            if r.status_code == 200:
                st.json(r.json())
            else:
                st.error(r.text)
