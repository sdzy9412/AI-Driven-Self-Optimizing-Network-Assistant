import json
from datetime import datetime

def lambda_handler(event, context=None):
    """Simulated Lambda executor for applying the recommended action."""
    record = event.get("record")
    action = record.get("action_applied")
    confidence = record.get("ai_confidence")

    result = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "cell_id": record.get("cell_id"),
        "action_executed": action,
        "ai_confidence": confidence,
        "status": "executed",
        "message": f"Lambda executed action '{action}' with confidence {confidence}"
    }

    print(json.dumps(result, indent=2))
    return result
