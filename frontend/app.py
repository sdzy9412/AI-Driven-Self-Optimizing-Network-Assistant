import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
from datetime import datetime, timedelta
import numpy as np
import os
from pathlib import Path
import time

# Set page configuration
st.set_page_config(page_title="Network Status Monitoring", layout="wide")

# Center align title
st.markdown("""
    <style>
    h1 {
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title(" Network Cell Status Monitoring Dashboard")

# Load base data
@st.cache_data
def load_base_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(script_dir, '../data/mock_metrics.json'),
        os.path.join(script_dir, '../../data/mock_metrics.json'),
        'data/mock_metrics.json',
        '../data/mock_metrics.json',
        'mock_metrics.json',
    ]
    
    data_file = None
    for path in possible_paths:
        p = Path(path)
        if p.exists():
            data_file = p
            break
    
    if data_file is None:
        st.error("❌ Data file mock_metrics.json not found")
        return pd.DataFrame()
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        # Replace cell IDs
        if 'cell_id' in df.columns:
            df['cell_id'] = df['cell_id'].replace('cell-A01', 'cell-RAN')
            df['cell_id'] = df['cell_id'].replace('cell-B17', 'cell-Transport')
        return df
    except Exception as e:
        st.error(f"❌ Error loading data file: {e}")
        return pd.DataFrame()

# Initialize session state
if 'base_data' not in st.session_state:
    st.session_state.base_data = load_base_data()

if 'realtime_data' not in st.session_state:
    st.session_state.realtime_data = st.session_state.base_data.copy()

if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

if 'data_points_count' not in st.session_state:
    st.session_state.data_points_count = len(st.session_state.base_data)

# Initialize last timestamp (from base data)
if 'last_timestamp' not in st.session_state:
    if not st.session_state.base_data.empty and 'timestamp' in st.session_state.base_data.columns:
        # Get maximum timestamp from all data
        max_timestamp = st.session_state.base_data['timestamp'].max()
        st.session_state.last_timestamp = max_timestamp
    else:
        # If no base data, use current time minus some seconds as starting point
        st.session_state.last_timestamp = datetime.now() - timedelta(seconds=60)

# Initialize time window display range (initial 10 minutes, max 20 minutes)
if 'view_window_minutes' not in st.session_state:
    st.session_state.view_window_minutes = 10  # Initial display 10 minutes

if 'start_time' not in st.session_state:
    # Get data start time (08:00:00)
    if not st.session_state.base_data.empty and 'timestamp' in st.session_state.base_data.columns:
        st.session_state.start_time = st.session_state.base_data['timestamp'].min()
    else:
        st.session_state.start_time = datetime.now() - timedelta(minutes=30)

# Get data end time (08:30:00), used to limit data generation beyond this time
if 'max_data_timestamp' not in st.session_state:
    if not st.session_state.base_data.empty and 'timestamp' in st.session_state.base_data.columns:
        st.session_state.max_data_timestamp = st.session_state.base_data['timestamp'].max()
    else:
        st.session_state.max_data_timestamp = datetime.now()

# Status color mapping
STATUS_COLORS = {
    'normal': 'rgba(0, 123, 255, 0.8)',      # Blue with transparency
    'incident': 'rgba(220, 53, 69, 0.8)',    # Red with transparency
    'optimized': 'rgba(40, 167, 69, 0.8)'    # Green with transparency
}

STATUS_FILL_COLORS = {
    'normal': 'rgba(0, 123, 255, 0.2)',      # Fill color more transparent
    'incident': 'rgba(220, 53, 69, 0.2)',
    'optimized': 'rgba(40, 167, 69, 0.2)'
}

STATUS_LABELS = {
    'normal': 'Normal',
    'incident': 'Incident',
    'optimized': 'AI Optimized'
}

# Metric information
METRIC_INFO = {
    'latency_ms': {'name': 'Latency', 'unit': 'ms', 'lower_better': True},
    'packet_loss': {'name': 'Packet Loss', 'unit': '%', 'lower_better': True},
    'throughput_mbps': {'name': 'Throughput', 'unit': 'Mbps', 'lower_better': False},
    'utilization_pct': {'name': 'Utilization', 'unit': '%', 'lower_better': False},
    'energy_kwh': {'name': 'Energy Consumption', 'unit': 'kWh', 'lower_better': True}
}

# Sidebar controls
st.sidebar.header("Control Panel")

if st.session_state.base_data.empty:
    st.warning("⚠️ Data is empty, please check the data file")
    st.stop()

selected_cell = st.sidebar.selectbox("Select Network Cell", st.session_state.base_data['cell_id'].unique())
selected_metric = st.sidebar.selectbox(
    "Select Monitoring Metric",
    ['latency_ms', 'packet_loss', 'throughput_mbps', 'utilization_pct', 'energy_kwh']
)

# Real-time data simulation function
def generate_realtime_data():
    """Generate simulated real-time data - based on timestamp increment"""
    # Increment based on previous timestamp (increase by 30 seconds each time, consistent with data file interval)
    if 'last_timestamp' in st.session_state:
        new_timestamp = st.session_state.last_timestamp + timedelta(seconds=30)
    else:
        # If no record, use maximum timestamp from base data
        if not st.session_state.base_data.empty:
            new_timestamp = st.session_state.base_data['timestamp'].max() + timedelta(seconds=30)
        else:
            new_timestamp = datetime.now()
    
    # Get latest data for currently selected cell
    cell_data = st.session_state.realtime_data[
        st.session_state.realtime_data['cell_id'] == selected_cell
    ]
    
    if len(cell_data) == 0:
        # If no data, use base data
        base_cell_data = st.session_state.base_data[
            st.session_state.base_data['cell_id'] == selected_cell
        ]
        if len(base_cell_data) > 0:
            latest_data = base_cell_data.iloc[-1].copy()
        else:
            # If still no data, create default data
            latest_data = pd.Series({
                'timestamp': new_timestamp - timedelta(seconds=30),
                'cell_id': selected_cell,
                'region': 'eu-west-1',
                'latency_ms': 50,
                'packet_loss': 0.1,
                'throughput_mbps': 120,
                'utilization_pct': 45,
                'energy_kwh': 2.5,
                'status': 'normal',
                'action_applied': None,
                'ai_confidence': None
            })
    else:
        latest_data = cell_data.iloc[-1].copy()
    
    # Create new data point
    new_point = latest_data.copy()
    new_point['timestamp'] = new_timestamp
    
    # Update last timestamp
    st.session_state.last_timestamp = new_timestamp
    
    # Get current status
    current_status = new_point['status']
    current_latency = latest_data.get('latency_ms', 50)
    
    # Calculate time difference based on timestamp (for optimized state recovery judgment)
    if len(cell_data) > 1:
        cell_data_sorted = cell_data.sort_values('timestamp')
        last_change_idx = len(cell_data_sorted) - 1
        for i in range(len(cell_data_sorted) - 2, -1, -1):
            if cell_data_sorted.iloc[i]['status'] != current_status:
                break
            last_change_idx = i
        
        if last_change_idx < len(cell_data_sorted):
            last_change_time = cell_data_sorted.iloc[last_change_idx]['timestamp']
            time_since_last_change = (new_timestamp - last_change_time).total_seconds()
        else:
            time_since_last_change = (new_timestamp - latest_data['timestamp']).total_seconds() if 'timestamp' in latest_data and pd.notna(latest_data['timestamp']) else 30
    elif len(cell_data) == 1:
        time_since_last_change = (new_timestamp - cell_data.iloc[0]['timestamp']).total_seconds()
    else:
        if 'timestamp' in latest_data and pd.notna(latest_data['timestamp']):
            time_since_last_change = (new_timestamp - latest_data['timestamp']).total_seconds()
        else:
            time_since_last_change = 30
    
    # First generate metric values based on current status (especially latency)
    # Normal status: latency 1~129ms
    # Incident status: latency >=140ms
    # Optimized status: latency reduced from >=140ms to 1~129ms
    if current_status == 'normal':
        # Normal status: latency between 1~129ms (with fluctuations, may occasionally approach boundary)
        base_latency = current_latency + np.random.uniform(-10, 15)
        # Limit within 1~129ms range, but allow small probability of fluctuation to abnormal range
        if base_latency > 129:
            # If exceeds 129ms, 30% probability continues to rise becoming abnormal (>=140ms), otherwise returns to normal range
            if np.random.random() < 0.3:  # 30% probability of incident
                new_point['latency_ms'] = np.random.uniform(140, 200)  # Incident range
            else:
                new_point['latency_ms'] = np.random.uniform(50, 120)  # Return to normal range
        else:
            new_point['latency_ms'] = max(1, min(129, base_latency))  # Keep within 1~129ms
        new_point['packet_loss'] = max(0, new_point.get('packet_loss', 0.1) + np.random.uniform(-0.05, 0.05))
        new_point['throughput_mbps'] = max(80, new_point.get('throughput_mbps', 120) + np.random.uniform(-5, 5))
        new_point['utilization_pct'] = max(10, min(90, new_point.get('utilization_pct', 45) + np.random.uniform(-3, 3)))
        new_point['energy_kwh'] = max(1.5, new_point.get('energy_kwh', 2.5) + np.random.uniform(-0.1, 0.1))
    elif current_status == 'incident':
        # Incident status: latency >=140ms (maintain incident or more severe)
        new_point['latency_ms'] = max(140, current_latency + np.random.uniform(-10, 50))
        new_point['packet_loss'] = max(1, min(15, new_point.get('packet_loss', 5) + np.random.uniform(-1, 1.5)))
        new_point['throughput_mbps'] = max(50, new_point.get('throughput_mbps', 100) + np.random.uniform(-10, 5))
        new_point['utilization_pct'] = max(60, min(98, new_point.get('utilization_pct', 85) + np.random.uniform(-5, 5)))
        new_point['energy_kwh'] = max(2.5, new_point.get('energy_kwh', 4) + np.random.uniform(-0.2, 0.3))
    else:  # optimized
        # Optimized status: latency should be in normal range (1~129ms), but may have some fluctuations
        new_point['latency_ms'] = max(1, min(129, current_latency + np.random.uniform(-15, 10)))
        new_point['packet_loss'] = max(0.5, min(8, new_point.get('packet_loss', 2) + np.random.uniform(-0.3, 0.5)))
        new_point['throughput_mbps'] = max(90, new_point.get('throughput_mbps', 125) + np.random.uniform(-5, 8))
        new_point['utilization_pct'] = max(30, min(85, new_point.get('utilization_pct', 65) + np.random.uniform(-4, 4)))
        new_point['energy_kwh'] = max(2, new_point.get('energy_kwh', 3) + np.random.uniform(-0.15, 0.2))
    
    # Determine status based on latency value (based on metric value, not time)
    # Normal status: latency 1~129ms
    # Incident status: latency >=140ms
    # Optimized status: after AI optimization, latency reduced from >=140ms to 1~129ms
    
    new_latency = new_point['latency_ms']
    
    if current_status == 'normal':
        # Normal status: if latency >=140ms, becomes incident
        if new_latency >= 140:
            new_point['status'] = 'incident'
            new_point['ai_confidence'] = round(np.random.uniform(0.7, 0.9), 2)
        else:
            new_point['status'] = 'normal'
            new_point['action_applied'] = None
            new_point['ai_confidence'] = None
    elif current_status == 'incident':
        # Incident status: if latency still >=140ms, maintain incident; if AI optimization reduces latency to <140ms (enters 1~129ms range), becomes optimized
        if new_latency >= 140:
            new_point['status'] = 'incident'
            # AI will attempt optimization with certain probability (but needs to wait for some time)
            if time_since_last_change > 20 and np.random.random() < 0.5:  # After 20 seconds, 50% probability AI optimization
                # AI optimization: reduce latency to normal range (1~129ms)
                new_point['latency_ms'] = np.random.uniform(50, 120)  # Normal latency range after optimization
                new_point['status'] = 'optimized'
                new_point['action_applied'] = np.random.choice(['traffic_steering', 'load_balancing'])
                new_point['ai_confidence'] = round(np.random.uniform(0.8, 0.95), 2)
            else:
                new_point['ai_confidence'] = round(np.random.uniform(0.7, 0.9), 2)
        else:
            # Latency has dropped to normal range (<140ms, should be 1~129ms), should become optimized status (AI has taken effect)
            # Ensure within normal range
            if new_latency < 140:
                new_point['latency_ms'] = np.random.uniform(50, 120)  # Ensure within 1~129ms range
            new_point['status'] = 'optimized'
            new_point['action_applied'] = np.random.choice(['traffic_steering', 'load_balancing'])
            new_point['ai_confidence'] = round(np.random.uniform(0.8, 0.95), 2)
    else:  # optimized
        # Optimized status: latency should be in normal range (1~129ms)
        if new_latency >= 140:
            # If latency is >=140ms again, optimization may have failed, revert to incident
            new_point['status'] = 'incident'
            new_point['action_applied'] = None
            new_point['ai_confidence'] = round(np.random.uniform(0.7, 0.9), 2)
        else:
            # Latency in normal range (<140ms), maintain optimized status
            new_point['status'] = 'optimized'
            # After some time, can recover to normal status (indicating issue resolved)
            if time_since_last_change > 60 and np.random.random() < 0.4:  # After 60 seconds, 40% probability returns to normal
                new_point['status'] = 'normal'
                new_point['action_applied'] = None
                new_point['ai_confidence'] = None
            else:
                new_point['action_applied'] = np.random.choice(['traffic_steering', 'load_balancing'])
                new_point['ai_confidence'] = round(np.random.uniform(0.8, 0.95), 2)
    
    return new_point

# Create area line chart
def create_area_chart(data, metric, cell_id):
    fig = go.Figure()
    
    metric_info = METRIC_INFO[metric]
    
    # Filter data for selected cell
    cell_data = data[data['cell_id'] == cell_id].sort_values('timestamp')
    
    # Draw area chart by status segments
    if len(cell_data) > 0:
        current_status = cell_data.iloc[0]['status']
        start_idx = 0
        # Track added statuses to ensure each status appears only once in legend
        seen_statuses = set()
        
        for i in range(1, len(cell_data) + 1):
            if i == len(cell_data) or cell_data.iloc[i]['status'] != current_status:
                end_idx = i
                
                # Get data for current segment
                segment_data = cell_data.iloc[start_idx:end_idx]
                
                # Determine if this is the first occurrence of this status
                is_first_occurrence = current_status not in seen_statuses
                if is_first_occurrence:
                    seen_statuses.add(current_status)
                
                # Add area chart
                fig.add_trace(go.Scatter(
                    x=segment_data['timestamp'],
                    y=segment_data[metric],
                    mode='lines',
                    line=dict(color=STATUS_COLORS[current_status], width=3),
                    fill='tozeroy',
                    fillcolor=STATUS_FILL_COLORS[current_status],
                    name=STATUS_LABELS[current_status],
                    legendgroup=current_status,  # Group same statuses together
                    showlegend=is_first_occurrence,  # Show legend only for first occurrence of status
                    hovertemplate=(
                        f"<b>{metric_info['name']}</b>: %{{y:.2f}} {metric_info['unit']}<br>" +
                        f"Status: {STATUS_LABELS[current_status]}<br>" +
                        "Time: %{x}<br>" +
                        "<extra></extra>"
                    )
                ))
                
                # Add markers at status change points
                if start_idx > 0 or (i == len(cell_data) and len(segment_data) > 0):
                    fig.add_trace(go.Scatter(
                        x=[segment_data.iloc[0]['timestamp']],
                        y=[segment_data.iloc[0][metric]],
                        mode='markers',
                        marker=dict(
                            color=STATUS_COLORS[current_status],
                            size=10,
                            symbol='circle',
                            line=dict(width=2, color='white')
                        ),
                        name=f"{STATUS_LABELS[current_status]} Start",
                        hovertemplate=(
                            f"Status Changed to: {STATUS_LABELS[current_status]}<br>" +
                            f"{metric_info['name']}: %{{y:.2f}} {metric_info['unit']}<br>" +
                            "Time: %{x}<br>" +
                            "<extra></extra>"
                        ),
                        showlegend=False
                    ))
                
                start_idx = i
                if i < len(cell_data):
                    current_status = cell_data.iloc[i]['status']
    
    # Chart layout
    fig.update_layout(
        title=f"{cell_id} - {metric_info['name']} Status Monitoring (Real-time Area Chart - Auto-update based on timestamp)",
        xaxis_title="Timestamp",
        yaxis_title=f"{metric_info['name']} ({metric_info['unit']})",
        hovermode='x unified',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='rgba(240,240,240,0.8)',
        font=dict(size=12),
        # Ensure time axis displays correctly
        xaxis=dict(
            type='date',
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGrey',
            tickformat='%H:%M:%S'
        )
    )
    
    # Add grid lines
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    
    # If too many data points, automatically adjust display range (show recent data points)
    if len(cell_data) > 50:
        # Only show last 50 data points to maintain responsiveness
        visible_range_start = cell_data['timestamp'].iloc[-50]
        fig.update_xaxes(range=[visible_range_start, cell_data['timestamp'].max()])
    
    return fig

# Create metric cards
def create_metric_cards(data, cell_id):
    cell_data = data[data['cell_id'] == cell_id]
    if len(cell_data) == 0:
        st.warning(f"No data found for {cell_id}")
        return
    
    current_status = cell_data.iloc[-1]['status']
    latest_data = cell_data.iloc[-1]
    
    # Define card style CSS
    card_style = """
    <style>
    .metric-card-container {
        background-color: #ffffff;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        margin: 5px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .metric-card-container:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }
    .metric-label {
        font-size: 14px;
        color: #666666;
        margin-bottom: 8px;
        font-weight: 500;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #000000;
        margin: 8px 0;
    }
    .metric-unit {
        font-size: 18px;
        color: #888888;
        font-weight: normal;
    }
    </style>
    """
    
    st.markdown(card_style, unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(
            f"""
            <div class="metric-card-container">
                <div class="metric-label">Current Latency</div>
                <div class="metric-value">{latest_data['latency_ms']:.1f}<span class="metric-unit"> ms</span></div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div class="metric-card-container">
                <div class="metric-label">Packet Loss</div>
                <div class="metric-value">{latest_data['packet_loss']:.2f}<span class="metric-unit">%</span></div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div class="metric-card-container">
                <div class="metric-label">Throughput</div>
                <div class="metric-value">{latest_data['throughput_mbps']:.1f}<span class="metric-unit"> Mbps</span></div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            f"""
            <div class="metric-card-container">
                <div class="metric-label">Utilization</div>
                <div class="metric-value">{latest_data['utilization_pct']:.1f}<span class="metric-unit">%</span></div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col5:
        status_color = STATUS_COLORS[current_status].replace('0.8', '1')  # Use opaque color
        st.markdown(
            f"""
            <div class="metric-card-container" style="background-color: {status_color}; border-color: {status_color};">
                <div class="metric-label" style="color: rgba(255,255,255,0.9);">Current Status</div>
                <div class="metric-value" style="color: white; font-size: 28px;">{STATUS_LABELS[current_status]}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

# Main interface layout
st.sidebar.header("Real-time Control")
# Real-time data simulation is always enabled (default True)
realtime_enabled = True
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 1, 10, 3)

# Create metric cards
create_metric_cards(st.session_state.realtime_data, selected_cell)

st.divider()

# Create dedicated real-time chart container
st.subheader("Real-time Monitoring Area Chart")

# Use container to isolate chart area
chart_container = st.container()

with chart_container:
    # Create chart within container
    fig = create_area_chart(st.session_state.realtime_data, selected_metric, selected_cell)
    st.plotly_chart(fig, use_container_width=True)

# Display real-time status information
status_col1, status_col2, status_col3 = st.columns(3)
cell_data_display = st.session_state.realtime_data[st.session_state.realtime_data['cell_id'] == selected_cell]
with status_col1:
    st.info(f"Data Points: {len(cell_data_display)}")
with status_col2:
    if realtime_enabled:
        st.success("🟢 Real-time Updating")
    else:
        st.warning("🟡 Static Mode")
with status_col3:
    if not cell_data_display.empty and 'timestamp' in cell_data_display.columns:
        time_range = f"{cell_data_display['timestamp'].min().strftime('%H:%M:%S')} - {cell_data_display['timestamp'].max().strftime('%H:%M:%S')}"
        st.info(f"Time Range: {time_range}")

# Display event timeline
def create_timeline(data, cell_id):
    st.subheader(" Event Timeline")
    
    cell_data = data[data['cell_id'] == cell_id]
    timeline_data = []
    
    for _, row in cell_data.iterrows():
        if row['status'] == 'incident' or row['status'] == 'optimized':
            timeline_data.append({
                'Time': row['timestamp'].strftime('%H:%M:%S'),
                'Event': '🚨 Incident Detected' if row['status'] == 'incident' else f"✅ AI Optimization: {row['action_applied']}",
                'Status': STATUS_LABELS[row['status']],
                'Confidence': f"{row['ai_confidence']:.2f}" if pd.notna(row['ai_confidence']) else 'N/A'
            })
    
    if timeline_data:
        timeline_df = pd.DataFrame(timeline_data)
        st.dataframe(timeline_df, use_container_width=True)
    else:
        st.info("No incident or optimization events")

create_timeline(st.session_state.realtime_data, selected_cell)

# Display raw data (collapsible)
with st.expander("View Raw Data"):
    cell_data = st.session_state.realtime_data[st.session_state.realtime_data['cell_id'] == selected_cell]
    st.dataframe(cell_data, use_container_width=True)

# Real-time update logic
if realtime_enabled:
    # Generate new real-time data (based on timestamp increment)
    new_data = generate_realtime_data()
    
    # Ensure new_data is in dictionary format
    if isinstance(new_data, pd.Series):
        new_data = new_data.to_dict()
    
    new_df = pd.DataFrame([new_data])
    
    # Ensure timestamp column is datetime type
    if 'timestamp' in new_df.columns:
        new_df['timestamp'] = pd.to_datetime(new_df['timestamp'])
    
    # Update real-time data (keep last 200 data points to ensure complete time series visibility)
    st.session_state.realtime_data = pd.concat([
        st.session_state.realtime_data, new_df
    ], ignore_index=True).tail(200)
    
    # Ensure data is sorted by time
    if 'timestamp' in st.session_state.realtime_data.columns:
        st.session_state.realtime_data = st.session_state.realtime_data.sort_values('timestamp').reset_index(drop=True)
    
    st.session_state.last_update = datetime.now()
    st.session_state.data_points_count += 1
    
    # Use Streamlit's auto rerun feature for partial refresh
    time.sleep(refresh_interval)
    st.rerun()
