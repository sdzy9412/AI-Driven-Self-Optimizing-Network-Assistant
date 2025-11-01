
---

### `/README.md`
```md
# AI-Driven Self-Optimizing Network Assistant

## Overview
This project demonstrates an autonomous, explainable, and safe closed loop for network optimization
using **Strands Agents**, **Amazon Bedrock AgentCore**, and **AWS Lambda**.

It brings together RAN and Transport domains to show how agents can detect incidents, reason about causes,
apply optimization actions, and verify KPI improvement.

## Architecture
1. **Telemetry Layer** – `/data/mock_metrics.json`  
   Unified telemetry snapshot: latency, packet loss, utilization, energy.
2. **Agent Reasoning Layer** – `agentcore_output.json`  
   Bedrock AgentCore analyzes incident records and outputs root cause + action + confidence.
3. **Execution Layer** – `/backend/lambda_handler.py`  
   Lambda safely executes actions with rollback window.
4. **Visualization Layer** – `/app_streamlit.py`  
   Streamlit dashboard shows before/after KPIs.
5. **Audit & Learning** – Logs stored for transparency and future model fine-tuning.

## Key Results
| KPI | Before (Incident) | After (Optimized) | Improvement |
|-----|-------------------|-------------------|--------------|
| Latency (ms) | 310 → 140 | 270 → 115 | −55% |
| Packet Loss (%) | 5.8 → 2.2 | 4.9 → 1.9 | −60% |
| Energy (kWh) | 3.9 → 3.1 | 4.4 → 3.5 | −20% |
| MTTR | ~30 min (manual) | < 5 min (agent) | −83% |

## Deployed AWS Architecture (Live Demo)

The self-healing loop is partially deployed on AWS using **CloudFormation**:

- **Amazon S3** – stores unified telemetry snapshots (`mock_metrics.json`, `before_after_metrics.csv`).
- **AWS Lambda (`apply_recovery_action`)** – executes AI-recommended actions such as `traffic_steering` and logs auditable records.
- **Amazon DynamoDB (`NetworkChangeAudit`)** – stores each executed change with timestamp, action, confidence, and rollback window.

![Architecture](docs/architecture_diagram.png)

**Validation results:**
- ✅ Lambda executed successfully and returned a JSON response.  
- ✅ DynamoDB recorded an audit item automatically.  
- ✅ All resources were created via a single CloudFormation stack (`infra/template.yaml`).

> This confirms that the execution & audit leg of our self-healing network runs live inside AWS.


## How to Run
```bash
pip install streamlit pandas
streamlit run app_streamlit.py
