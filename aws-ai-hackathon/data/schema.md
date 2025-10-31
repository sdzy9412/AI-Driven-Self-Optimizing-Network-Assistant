# Telemetry Schema (DO NOT CHANGE FIELD NAMES)

## Fields
- `timestamp` (string, ISO 8601): Time when metrics were collected.
- `cell_id` (string): Network node / cell / site identifier, e.g. `"cell-A01"`.
- `region` (string): Deployment region, e.g. `"eu-west-1"`.
- `latency_ms` (number): Average round-trip latency in milliseconds. Lower = better.
- `packet_loss` (number): Packet loss percentage. Lower = better.
- `throughput_mbps` (number): Throughput in Mbps. Higher = better.
- `utilization_pct` (number): Resource utilization (%) such as bandwidth or CPU. Too high = overload.
- `energy_kwh` (number): Energy consumption (kWh).
- `status` (string): `"normal"` / `"incident"` / `"optimized"`.
- `action_applied` (string | null): Optimization action taken, e.g. `"load_balancing"` or `"traffic_steering"`.
- `ai_confidence` (number | null): Agent confidence (0–1).

## Modeling Assumptions
- Only two cells are tracked: `cell-A01` and `cell-B17`.
- Each cell has three phases: `normal → incident → optimized`.
- “Optimized” = improved but not magically perfect.

## Contract
All modules (AgentCore / Lambda / Dashboard) must follow this schema.  
Changing or renaming any field breaks integration.
