#!/usr/bin/env python3
"""
Simple AI-Driven Network Optimization Demo
Clean implementation following AWS AgentCore Runtime tutorial
"""
import asyncio
import json
import boto3

class SimpleNetworkAI:
    """Minimal AI network optimization demo"""
    
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    def analyze_incident(self, incident: dict) -> dict:
        """Analyze network incident with Bedrock"""
        
        prompt = f"""
Network Incident Analysis:
- Cell: {incident['cell_id']}
- Latency: {incident['latency_ms']}ms
- Utilization: {incident['utilization_pct']}%
- Packet Loss: {incident['packet_loss']}%

Recommend action: traffic_steering or load_balancing
Provide confidence (0-1) and reasoning.

Respond in JSON: {{"action": "...", "confidence": 0.0, "reasoning": "..."}}
"""
        
        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 300,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            
            result = json.loads(response['body'].read())
            ai_text = result['content'][0]['text']
            
            # Extract JSON
            json_start = ai_text.find("{")
            json_end = ai_text.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(ai_text[json_start:json_end])
            
        except Exception as e:
            print(f"Bedrock error: {e}")
        
        # Fallback
        return {
            "action": "load_balancing",
            "confidence": 0.75,
            "reasoning": "Rule-based fallback analysis"
        }
    
    def execute_action(self, action: str, cell_id: str) -> dict:
        """Simulate MCP tool execution"""
        
        if action == "traffic_steering":
            return {
                "action": "traffic_steering",
                "cell_id": cell_id,
                "status": "executed",
                "impact": {
                    "latency_reduction": "28%",
                    "packet_loss_reduction": "32%"
                }
            }
        else:  # load_balancing
            return {
                "action": "load_balancing", 
                "cell_id": cell_id,
                "status": "executed",
                "impact": {
                    "utilization_reduction": "25%",
                    "energy_savings": "15%"
                }
            }

def main():
    print("🚀 AI-Driven Network Optimization Demo")
    print("=" * 45)
    
    # Load test data
    with open('../data/mock_metrics.json', 'r') as f:
        data = json.load(f)
    
    incidents = [m for m in data if m.get('status') == 'incident']
    print(f"📊 Processing {len(incidents)} incidents")
    
    ai = SimpleNetworkAI()
    
    for incident in incidents:
        cell_id = incident['cell_id']
        print(f"\n🔍 {cell_id}:")
        print(f"   Latency: {incident['latency_ms']}ms")
        print(f"   Utilization: {incident['utilization_pct']}%")
        
        # AI Analysis
        analysis = ai.analyze_incident(incident)
        print(f"\n🧠 AI Decision:")
        print(f"   Action: {analysis['action']}")
        print(f"   Confidence: {analysis['confidence']:.1%}")
        print(f"   Reasoning: {analysis['reasoning']}")
        
        # Execute
        result = ai.execute_action(analysis['action'], cell_id)
        print(f"\n⚡ Execution:")
        print(f"   Status: {result['status']}")
        for key, value in result['impact'].items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
    
    print(f"\n✅ Demo completed!")

if __name__ == "__main__":
    main()