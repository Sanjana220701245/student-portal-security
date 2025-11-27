import os
import json
from openai import AzureOpenAI

class SecurityAlertSummarizer:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key="D1R1vM3xKv275a6zcCPeGpoICrWakPUvRMUDrOFLbeXTedFXzpG6JQQJ99BJACqBBLyXJ3w3AAABACOGf7Dy",
            api_version="2024-12-01-preview",
            azure_endpoint="https://student-security-openai.openai.azure.com/openai/deployments/Alert-Summarizer/embeddings?api-version=2023-05-15"
        )
        self.deployment_name = "Alert-Summarizer"
    
    def summarize_alert(self, alert_data):
        """Generate AI summary of security alert"""
        
        prompt = f"""
        Analyze this security alert and provide a clear, actionable summary:
        
        Alert Name: {alert_data['alert_name']}
        Severity: {alert_data['severity']}
        Description: {alert_data['description']}
        Affected User: {alert_data.get('username', 'Unknown')}
        Source IP: {alert_data.get('ip_address', 'Unknown')}
        Failed Attempts: {alert_data.get('failed_attempts', 0)}
        
        Provide:
        1. Threat Summary (2-3 sentences explaining what happened)
        2. Potential Impact (what could happen if not addressed)
        3. Recommended Actions (3-5 specific steps to take)
        4. Overall Risk Assessment (Low/Medium/High/Critical with brief justification)
        
        Format your response clearly with headers.
        """
        
        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=[
                {"role": "system", "content": "You are a cybersecurity expert helping IT administrators understand and respond to security threats."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    def explain_threat_pattern(self, attack_type):
        """Explain different attack patterns"""
        
        prompt = f"""
        Explain the following security threat pattern in simple terms for a university IT administrator:
        
        Attack Type: {attack_type}
        
        Provide:
        1. What is this attack? (2-3 sentences)
        2. Why do attackers use this method?
        3. How to detect it in logs?
        4. Best prevention strategies for student portals?
        
        Keep it practical and actionable.
        """
        
        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=[
                {"role": "system", "content": "You are a cybersecurity educator explaining threats to university IT staff."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.5
        )
        
        return response.choices[0].message.content

# Demo usage
if __name__ == "__main__":
    summarizer = SecurityAlertSummarizer()
    
    # Sample alert data (from Sentinel)
    sample_alert = {
        "alert_name": "Multiple Failed Login Attempts Detected",
        "severity": "High",
        "description": "Potential brute force attack detected",
        "username": "ST001",
        "ip_address": "192.168.1.100",
        "failed_attempts": 12
    }
    
    print("🤖 AI-Generated Alert Summary:")
    print("=" * 60)
    summary = summarizer.summarize_alert(sample_alert)
    print(summary)
    print("\n" + "=" * 60)
    
    print("\n📚 Threat Pattern Explanation:")
    print("=" * 60)
    explanation = summarizer.explain_threat_pattern("Brute Force Attack")
    print(explanation)