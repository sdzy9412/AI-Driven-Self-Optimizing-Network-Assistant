# lambda_s3_handler.py
# Handler: index.lambda_handler
import json
import os
import boto3
import uuid
from datetime import datetime, timezone
from agentcore_simulator import simulate_agent_decision

s3 = boto3.client("s3")
dynamodb = boto3.client("dynamodb")

AUDIT_TABLE = os.environ.get("AUDIT_TABLE_NAME", "NetworkChangeAudit")
AUDIT_S3_PREFIX = os.environ.get("AUDIT_S3_PREFIX", "logs/audit")
BUCKET = os.environ.get("TELEMETRY_BUCKET_NAME")

def read_s3_json(bucket, key):
    resp = s3.get_object(Bucket=bucket, Key=key)
    body = resp["Body"].read()
    return json.loads(body)

def put_dynamo_item(item):
    # item is a dict of string -> native types
    dynamodb.put_item(
        TableName=AUDIT_TABLE,
        Item={
            "change_id": {"S": item["change_id"]},
            "timestamp_utc": {"S": item["timestamp_utc"]},
            "cell_id": {"S": item["cell_id"]},
            "action_executed": {"S": item["action_executed"] or "none"},
            "ai_confidence": {"N": str(item.get("ai_confidence", 0.0))},
            "status": {"S": item.get("status", "executed")},
            "message": {"S": item.get("message", "")}
        }
    )

def append_audit_to_s3(bucket, audit_record):
    # load existing day file if exists, else create
    date = audit_record["timestamp_utc"][:10]  # YYYY-MM-DD
    key = f"{AUDIT_S3_PREFIX}/change_log_{date}.json"
    try:
        resp = s3.get_object(Bucket=bucket, Key=key)
        data = json.loads(resp["Body"].read())
    except s3.exceptions.NoSuchKey:
        data = {"execution_date": date, "total_actions": 0, "actions": []}

    data["actions"].append(audit_record)
    data["total_actions"] = len(data["actions"])
    s3.put_object(Bucket=bucket, Key=key, Body=json.dumps(data, indent=2), ContentType="application/json")
    return key

def process_record(record):
    # record is a telemetry dict or array
    if isinstance(record, list):
        # process list -> iterate
        for r in record:
            process_record(r)
        return

    status = record.get("status", "").lower()
    if status != "incident":
        # nothing to do
        return {"skipped": True, "reason": "not incident", "cell_id": record.get("cell_id")}

    # call agentcore simulator
    decision = simulate_agent_decision(record)

    change_id = str(uuid.uuid4())
    ts = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
    audit = {
        "change_id": change_id,
        "timestamp_utc": ts,
        "cell_id": record.get("cell_id"),
        "network_layer": "RAN" if record.get("cell_id", "").startswith("cell-A") else "Transport",
        "detected_issue": {
            "latency_ms": record.get("latency_ms"),
            "packet_loss": record.get("packet_loss"),
            "utilization_pct": record.get("utilization_pct"),
            "root_cause": decision["root_cause"]
        },
        "ai_decision": {
            "recommended_action": decision["recommended_action"],
            "ai_confidence": decision["confidence"],
            "rollback_window_min": decision["rollback_window_min"]
        },
        "lambda_execution": {
            "status": "executed",
            "result": "success",
            "message": f"Lambda executed action '{decision['recommended_action']}'"
        },
        "post_action_metrics": {
            # in demo, we don't actually change network state; but we can pick the next 'optimized' sample if available
            "latency_ms": None,
            "packet_loss": None,
            "utilization_pct": None,
            "energy_kwh": None
        }
    }

    # write to DynamoDB
    put_dynamo_item({
        "change_id": audit["change_id"],
        "timestamp_utc": audit["timestamp_utc"],
        "cell_id": audit["cell_id"],
        "action_executed": audit["ai_decision"]["recommended_action"],
        "ai_confidence": audit["ai_decision"]["ai_confidence"] if "ai_confidence" in audit["ai_decision"] else audit["ai_decision"]["ai_confidence"],
        "status": audit["lambda_execution"]["status"],
        "message": audit["lambda_execution"]["message"]
    })

    # append daily audit JSON into S3 (human readable)
    append_audit_to_s3(BUCKET, audit)

    return {"change_id": change_id, "cell_id": audit["cell_id"], "action": audit["ai_decision"]["recommended_action"]}

def lambda_handler(event, context):
    """
    Expect S3 event or test event:
    - S3 event: records[].s3.bucket.name / object.key
    - test event: { "bucket": "...", "key": "data/telemetry_001.json" }
    """
    # support test event
    if "Records" in event and event["Records"] and "s3" in event["Records"][0]:
        rec = event["Records"][0]
        bucket = rec["s3"]["bucket"]["name"]
        key = rec["s3"]["object"]["key"]
    else:
        bucket = event.get("bucket", BUCKET)
        key = event.get("key")

    if not bucket or not key:
        return {"error": "missing bucket/key"}

    obj = read_s3_json(bucket, key)
    result = process_record(obj)
    return {"processed": result}
