# sim_uploader.py
# Usage: python sim_uploader.py
# Requirements: pip install boto3 python-dateutil

import boto3
import json
import time
from datetime import datetime, timezone, timedelta

# CONFIG - change these
BUCKET = "self-healing-network-telemetry-demo"   # <--- change to your bucket name
PREFIX = "data"
SLEEP_SECONDS = 3   # seconds between uploads (short for demo)
LOOP = False        # set True to continuously loop over timeline

s3 = boto3.client("s3")

# timeline: list of telemetry snapshots (you can expand)
timeline = [
    # normal for both cells
    {
      "timestamp": "2025-11-01T07:50:00Z",
      "cell_id": "cell-A01",
      "region": "eu-west-1",
      "latency_ms": 50,
      "packet_loss": 0.1,
      "throughput_mbps": 122,
      "utilization_pct": 45,
      "energy_kwh": 2.5,
      "status": "normal",
      "action_applied": None,
      "ai_confidence": None
    },
    {
      "timestamp": "2025-11-01T07:50:00Z",
      "cell_id": "cell-B17",
      "region": "eu-west-1",
      "latency_ms": 53,
      "packet_loss": 0.15,
      "throughput_mbps": 208,
      "utilization_pct": 48,
      "energy_kwh": 2.8,
      "status": "normal",
      "action_applied": None,
      "ai_confidence": None
    },
    # the timeline you already have (normal -> incident -> optimized)
    {
      "timestamp": "2025-11-01T08:00:00Z",
      "cell_id": "cell-A01",
      "region": "eu-west-1",
      "latency_ms": 48,
      "packet_loss": 0.1,
      "throughput_mbps": 120,
      "utilization_pct": 42,
      "energy_kwh": 2.3,
      "status": "normal",
      "action_applied": None,
      "ai_confidence": None
    },
    {
      "timestamp": "2025-11-01T08:05:00Z",
      "cell_id": "cell-A01",
      "region": "eu-west-1",
      "latency_ms": 310,
      "packet_loss": 5.8,
      "throughput_mbps": 118,
      "utilization_pct": 91,
      "energy_kwh": 3.9,
      "status": "incident",
      "action_applied": None,
      "ai_confidence": 0.81
    },
    {
      "timestamp": "2025-11-01T08:10:00Z",
      "cell_id": "cell-A01",
      "region": "eu-west-1",
      "latency_ms": 140,
      "packet_loss": 2.2,
      "throughput_mbps": 125,
      "utilization_pct": 69,
      "energy_kwh": 3.1,
      "status": "optimized",
      "action_applied": "traffic_steering",
      "ai_confidence": 0.84
    },
    {
      "timestamp": "2025-11-01T08:15:00Z",
      "cell_id": "cell-B17",
      "region": "eu-west-1",
      "latency_ms": 55,
      "packet_loss": 0.2,
      "throughput_mbps": 210,
      "utilization_pct": 50,
      "energy_kwh": 2.9,
      "status": "normal",
      "action_applied": None,
      "ai_confidence": None
    },
    {
      "timestamp": "2025-11-01T08:20:00Z",
      "cell_id": "cell-B17",
      "region": "eu-west-1",
      "latency_ms": 270,
      "packet_loss": 4.9,
      "throughput_mbps": 205,
      "utilization_pct": 88,
      "energy_kwh": 4.4,
      "status": "incident",
      "action_applied": None,
      "ai_confidence": 0.76
    },
    {
      "timestamp": "2025-11-01T08:25:00Z",
      "cell_id": "cell-B17",
      "region": "eu-west-1",
      "latency_ms": 115,
      "packet_loss": 1.9,
      "throughput_mbps": 215,
      "utilization_pct": 63,
      "energy_kwh": 3.5,
      "status": "optimized",
      "action_applied": "load_balancing",
      "ai_confidence": 0.82
    }
]

def upload_snapshot(obj, idx):
    key = f"{PREFIX}/telemetry_{idx:03d}.json"
    body = json.dumps(obj)
    print(f"[upload] -> s3://{BUCKET}/{key}")
    s3.put_object(Bucket=BUCKET, Key=key, Body=body, ContentType="application/json")
    return key

def main():
    idx = 0
    while True:
        for rec in timeline:
            idx += 1
            upload_snapshot(rec, idx)
            time.sleep(SLEEP_SECONDS)
        if not LOOP:
            break
    print("Done uploading timeline.")

if __name__ == "__main__":
    main()
