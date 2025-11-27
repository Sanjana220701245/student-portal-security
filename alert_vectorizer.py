import os
import numpy as np
import faiss
from sklearn.cluster import KMeans
from openai import AzureOpenAI

# Step 1: Initialize Azure OpenAI Client
class AlertVectorizer:
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
        return response.data[0].embedding

# Step 2: Sample Alerts
sample_alerts = [
    "Multiple failed login attempts from IP 192.168.1.100 targeting user ST001",
    "Suspicious PowerShell activity detected on endpoint WIN-22X",
    "Phishing email reported by user ST045 with malicious link",
    "Unusual outbound traffic from server SRV-DB01",
    "Privilege escalation attempt detected on Linux host LNX-01"
]

# Step 3: Vectorize Alerts
vectorizer = AlertVectorizer()
embeddings = [np.array(vectorizer.get_embedding(alert), dtype='float32') for alert in sample_alerts]

# Step 4: Build FAISS Index
dimension = len(embeddings[0])
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

# Step 5: Similarity Search (Demo)
query = "Brute force login attempts detected on student portal"
query_vector = np.array([vectorizer.get_embedding(query)], dtype='float32')
D, I = index.search(query_vector, k=3)

print("\n🔍 Top 3 Similar Alerts:")
for rank, idx in enumerate(I[0]):
    print(f"{rank+1}. {sample_alerts[idx]} (Distance: {D[0][rank]:.4f})")

# Step 6: Threat Clustering
kmeans = KMeans(n_clusters=3, random_state=42)
labels = kmeans.fit_predict(np.array(embeddings))

print("\n🧠 Threat Clusters:")
for i, label in enumerate(labels):
    print(f"Alert {i+1}: {sample_alerts[i]} → Cluster {label}")
