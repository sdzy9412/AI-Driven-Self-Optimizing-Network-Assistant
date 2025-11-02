# agentcore_simulator.py
# Simple rule-based agent simulation for demo.

import random

def simulate_agent_decision(record):
    """
    Input: telemetry record dict
    Output: dict with root_cause, recommended_action, confidence, rollback_window_min
    """
    latency = record.get("latency_ms", 0)
    packet_loss = record.get("packet_loss", 0)
    cell = record.get("cell_id", "unknown")

    # Simple heuristics
    if latency > 200 and packet_loss >= 5:
        root_cause = "Excessive uplink congestion"
        recommended_action = "traffic_steering"
        confidence = round(0.75 + random.random() * 0.2, 2)
    elif latency > 200 and packet_loss < 5:
        root_cause = "Transport/backhaul congestion"
        recommended_action = "load_balancing"
        confidence = round(0.7 + random.random() * 0.2, 2)
    else:
        root_cause = "Unknown/No action"
        recommended_action = None
        confidence = 0.0

    return {
        "root_cause": root_cause,
        "recommended_action": recommended_action,
        "confidence": confidence,
        "rollback_window_min": 5
    }
