import numpy as np
import faiss
from openai import AzureOpenAI

# Step 1: Initialize Azure OpenAI Client
class InsiderThreatDetector:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key="D1R1vM3xKv275a6zcCPeGpoICrWakPUvRMUDrOFLbeXTedFXzpG6JQQJ99BJACqBBLyXJ3w3AAABACOGf7Dy",
            api_version="2023-05-15",
            azure_endpoint="https://student-security-openai.openai.azure.com/openai/deployments/Alert-Summarizer/embeddings?api-version=2023-05-15"
        )
        self.deployment_name = "Alert-Summarizer"

    def get_embedding(self, text):
        response = self.client.embeddings.create(
            model=self.deployment_name,
            input=text
        )
        return np.array(response.data[0].embedding, dtype='float32')

# Step 2: Define Suspicious Behavior Templates
threat_templates = [
    "User accessed sensitive files outside working hours",
    "Multiple privilege escalation attempts within short time",
    "Unusual data transfer to external IP",
    "Repeated access to HR records by non-HR staff",
    "Login from geographically distant location within 1 hour"
]

# Step 3: Embed Templates
detector = InsiderThreatDetector()
template_embeddings = [detector.get_embedding(text) for text in threat_templates]

# Step 4: Build FAISS Index
dimension = len(template_embeddings[0])
index = faiss.IndexFlatL2(dimension)
index.add(np.array(template_embeddings))

# Step 5: Incoming Log Entry
log_entry = "User ST045 downloaded 300MB of files from finance folder at 2:30 AM"
log_vector = detector.get_embedding(log_entry)

# Step 6: Similarity Search
D, I = index.search(np.array([log_vector]), k=1)
similarity_score = 1 / (1 + D[0][0])  # Convert L2 distance to similarity

# Step 7: Threshold-Based Flagging
threshold = 0.85
print("\n🔍 Log Entry:")
print(log_entry)
print("\n🧠 Closest Threat Template:")
print(threat_templates[I[0][0]])
print(f"\n📊 Similarity Score: {similarity_score:.4f}")

if similarity_score >= threshold:
    print("\n🚨 Potential Insider Threat Detected!")
else:
    print("\n✅ Log appears normal.")