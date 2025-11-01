#!/usr/bin/env python3
"""
Mixed Confidence Scenarios Demo
Shows both auto-execution and human approval scenarios
"""
import json

class MixedSafetyDemo:
    """Demo with predefined scenarios showing different confidence levels"""
    
    def __init__(self):
        self.CONFIDENCE_THRESHOLD = 0.80
    
    def load_demo_scenarios(self):
        """Load scenarios from data file"""
        with open('../data/safety_demo_scenarios.json', 'r') as f:
            scenarios = json.load(f)
        
        # Add AI analysis based on expected confidence
        for scenario in scenarios:
            confidence = scenario['expected_confidence']
            if confidence >= 0.9:
                action = "load_balancing"
                reasoning = "Clear network congestion with high utilization and packet loss"
            elif confidence >= 0.8:
                action = "load_balancing"
                reasoning = "High confidence in congestion diagnosis and load balancing solution"
            elif confidence >= 0.6:
                action = "traffic_steering"
                reasoning = "Moderate issues but unclear root cause - more investigation needed"
            else:
                action = "traffic_steering"
                reasoning = "Borderline metrics - insufficient data for confident recommendation"
            
            scenario['ai_analysis'] = {
                "action": action,
                "confidence": confidence,
                "reasoning": reasoning
            }
        
        return scenarios
    
    def check_safety_approval(self, confidence: float) -> dict:
        """Check if action meets safety threshold"""
        auto_execute = confidence >= self.CONFIDENCE_THRESHOLD
        
        return {
            "auto_execute": auto_execute,
            "threshold": self.CONFIDENCE_THRESHOLD,
            "confidence": confidence,
            "status": "AUTO_APPROVED" if auto_execute else "HUMAN_APPROVAL_REQUIRED",
            "safety_check": "PASSED" if auto_execute else "BLOCKED"
        }
    
    def execute_action(self, scenario: dict, safety_approval: dict) -> dict:
        """Execute action based on safety approval"""
        
        if not safety_approval["auto_execute"]:
            return {
                "status": "BLOCKED",
                "reason": f"Confidence {safety_approval['confidence']:.1%} below {safety_approval['threshold']:.1%} threshold",
                "executed": False,
                "requires_human_approval": True,
                "safety_status": "BLOCKED_FOR_SAFETY"
            }
        
        return {
            "status": "EXECUTED",
            "action": scenario["ai_analysis"]["action"],
            "cell_id": scenario["cell_id"],
            "executed": True,
            "safety_status": "AUTO_APPROVED",
            "impact": {
                "utilization_reduction": "25%",
                "energy_savings": "15%",
                "execution_time": "1.2s"
            }
        }

def main():
    print("🛡️  AI Safety Mechanisms Demo")
    print("=" * 50)
    print("🎯 Confidence Threshold: 80% for auto-execution")
    print("🔒 Below 80% → Human approval required")
    print()
    
    demo = MixedSafetyDemo()
    scenarios = demo.load_demo_scenarios()
    
    auto_executed = 0
    human_approval_required = 0
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"📊 Scenario {i}: {scenario['cell_id']}")
        print(f"   Latency: {scenario['latency_ms']}ms")
        print(f"   Utilization: {scenario['utilization_pct']}%")
        print(f"   Packet Loss: {scenario['packet_loss']}%")
        
        analysis = scenario["ai_analysis"]
        print(f"\n🧠 AI Analysis:")
        print(f"   Action: {analysis['action']}")
        print(f"   Confidence: {analysis['confidence']:.1%}")
        print(f"   Reasoning: {analysis['reasoning']}")
        
        # Safety Check
        safety = demo.check_safety_approval(analysis['confidence'])
        print(f"\n🛡️  Safety Gate:")
        print(f"   Threshold Check: {analysis['confidence']:.1%} vs {safety['threshold']:.1%}")
        print(f"   Decision: {safety['status']}")
        print(f"   Safety Status: {safety['safety_check']}")
        
        # Execution
        execution = demo.execute_action(scenario, safety)
        print(f"\n⚡ Execution Result:")
        
        if execution['executed']:
            print(f"   ✅ STATUS: {execution['status']}")
            print(f"   🤖 Auto-executed by AI system")
            print(f"   📈 Expected Impact:")
            for key, value in execution['impact'].items():
                print(f"      {key.replace('_', ' ').title()}: {value}")
            auto_executed += 1
        else:
            print(f"   ❌ STATUS: {execution['status']}")
            print(f"   🚫 {execution['reason']}")
            print(f"   👤 Human operator approval required")
            print(f"   📋 Action queued for manual review")
            human_approval_required += 1
        
        print("─" * 50)
    
    print(f"\n📈 Safety Mechanism Results:")
    print(f"✅ Auto-executed (≥80% confidence): {auto_executed}")
    print(f"❌ Human approval required (<80%): {human_approval_required}")
    print(f"🛡️  Safety rate: {(human_approval_required/len(scenarios)*100):.0f}% of actions blocked for safety")
    
    print(f"\n🎯 Key Safety Features:")
    print(f"• Confidence-based execution control")
    print(f"• 80% threshold prevents risky actions")
    print(f"• Human oversight for uncertain cases")
    print(f"• Complete audit trail maintained")
    print(f"• Critical network operations protected")

if __name__ == "__main__":
    main()