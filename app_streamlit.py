import streamlit as st
import pandas as pd

st.set_page_config(page_title="Self-Optimizing Network KPIs", layout="wide")

st.title("AI-Driven Self-Optimizing Network Assistant")
st.caption("Timeline: Normal → Incident → Optimized per cell")

# Load data
df = pd.read_csv("data/before_after_metrics.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Sidebar filters
cells = st.sidebar.multiselect(
    "Select cell(s):",
    options=sorted(df["cell_id"].unique()),
    default=sorted(df["cell_id"].unique())
)

metric = st.sidebar.selectbox(
    "Select metric for line chart:",
    options=["latency_ms", "packet_loss", "throughput_mbps", "utilization_pct", "energy_kwh"],
    index=0
)

filtered = df[df["cell_id"].isin(cells)]

# KPI cards for cell-A01 (example)
st.subheader("Before vs After Impact (cell-A01)")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Latency (ms)", value="140", delta="-170 vs 310 incident")
with col2:
    st.metric(label="Packet Loss (%)", value="2.2", delta="-3.6 pp vs 5.8 incident")
with col3:
    st.metric(label="Energy (kWh)", value="3.1", delta="-0.8 vs 3.9 incident")

st.divider()

st.subheader(f"Timeline: {metric}")
plot_df = (
    filtered[["timestamp", "cell_id", metric]]
    .pivot(index="timestamp", columns="cell_id", values=metric)
    .sort_index()
)

st.line_chart(plot_df)
st.caption("After the agent’s action, latency drops, packet loss decreases, and energy efficiency improves.")
