import json
import requests
import datetime
import hashlib
import hmac
import base64
import time
import os

class AzureLogSender:
    def __init__(self, config_file="config.json"):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.workspace_id = self.config['workspace_id'].strip()
        self.shared_key = self.config['shared_key'].strip()  # Remove any whitespace
        self.log_type = self.config['log_type']
        
        # Validate credentials before proceeding
        self.validate_credentials()
        
    def validate_credentials(self):
        """Validate Azure credentials format"""
        # Workspace ID should be a GUID (32 hex chars + 4 hyphens = 36 chars)
        if len(self.workspace_id) != 36:
            print(f"❌ ERROR: Workspace ID looks incorrect. Length: {len(self.workspace_id)} (should be 36)")
            print(f"Your workspace ID: {self.workspace_id}")
            raise ValueError("Invalid Workspace ID format")
        
        # Shared key should be base64 encoded (usually 88 characters)
        try:
            decoded = base64.b64decode(self.shared_key)
            print(f"✅ Shared key validated successfully (decoded to {len(decoded)} bytes)")
        except Exception as e:
            print(f"❌ ERROR: Shared key is not valid base64")
            print(f"Key length: {len(self.shared_key)} characters")
            print(f"Key preview: {self.shared_key[:20]}...")
            raise ValueError(f"Invalid shared key format: {e}")
        
        print(f"✅ Workspace ID validated: {self.workspace_id}")
    
    def build_signature(self, date, content_length, method, content_type, resource):
        """Build authorization signature for Azure Log Analytics"""
        x_headers = f"x-ms-date:{date}"
        string_to_hash = f"{method}\n{content_length}\n{content_type}\n{x_headers}\n{resource}"
        
        bytes_to_hash = bytes(string_to_hash, 'UTF-8')
        decoded_key = base64.b64decode(self.shared_key)
        encoded_hash = base64.b64encode(
            hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()
        ).decode()
        
        return f"SharedKey {self.workspace_id}:{encoded_hash}"

    def send_logs(self, log_data):
        """Send logs to Azure Log Analytics"""
        if not log_data:
            print("⚠️  No logs to send")
            return False
        
        # Prepare the data
        body = json.dumps(log_data)
        content_length = len(body)
        
        # Build headers - Fixed datetime deprecation warning
        rfc1123date = datetime.datetime.now(datetime.UTC).strftime('%a, %d %b %Y %H:%M:%S GMT')
        content_type = 'application/json'
        
        try:
            signature = self.build_signature(
                rfc1123date, content_length, 'POST', content_type, '/api/logs'
            )
        except Exception as e:
            print(f"❌ Error building signature: {e}")
            return False
        
        headers = {
            'content-type': content_type,
            'Authorization': signature,
            'Log-Type': self.log_type,
            'x-ms-date': rfc1123date
        }
        
        # Send to Azure
        uri = f"https://{self.workspace_id}.ods.opinsights.azure.com/api/logs?api-version=2016-04-01"
        
        print(f"📤 Sending {len(log_data)} log entries to Azure...")
        print(f"   Endpoint: {uri}")
        
        try:
            response = requests.post(uri, data=body, headers=headers, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ Successfully sent {len(log_data)} log entries to Azure")
                print(f"   Wait 5-10 minutes for data to appear in Log Analytics")
                return True
            else:
                print(f"❌ Failed to send logs")
                print(f"   Status Code: {response.status_code}")
                print(f"   Response: {response.text}")
                
                # Common error messages
                if response.status_code == 403:
                    print("   💡 TIP: Check your workspace key - it might be incorrect")
                elif response.status_code == 404:
                    print("   💡 TIP: Check your workspace ID - it might be incorrect")
                    
                return False
                
        except requests.exceptions.Timeout:
            print(f"❌ Request timeout - check your internet connection")
            return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection error - check your internet connection")
            return False
        except Exception as e:
            print(f"❌ Error sending logs to Azure: {str(e)}")
            return False

def read_local_logs(log_file="../backend/logs/login_attempts.json"):
    """Read logs from local file"""
    try:
        if not os.path.exists(log_file):
            print(f"❌ Log file not found: {log_file}")
            print(f"   Make sure you've generated some login attempts first!")
            return []
            
        with open(log_file, 'r') as f:
            logs = json.load(f)
            
        if not logs:
            print(f"⚠️  Log file is empty: {log_file}")
            print(f"   Generate some login attempts first by using the student portal")
            return []
            
        print(f"📄 Found {len(logs)} log entries in {log_file}")
        return logs
        
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing log file: {e}")
        return []
    except Exception as e:
        print(f"❌ Error reading log file: {e}")
        return []

def main():
    """Main function to send logs to Azure"""
    print("=" * 60)
    print("Azure Log Analytics - Log Sender")
    print("=" * 60)
    
    try:
        # Initialize sender (this will validate credentials)
        sender = AzureLogSender()
        
        # Read local logs
        logs = read_local_logs()
        
        if not logs:
            print("\n⚠️  No logs to send. Please:")
            print("   1. Start your student portal: python app.py")
            print("   2. Generate some login attempts")
            print("   3. Run this script again")
            return
        
        # Send logs in batches of 10 (Azure limit is 30MB per request)
        batch_size = 10
        total_sent = 0
        
        for i in range(0, len(logs), batch_size):
            batch = logs[i:i + batch_size]
            
            print(f"\n📦 Batch {i//batch_size + 1} of {(len(logs)-1)//batch_size + 1}")
            
            if sender.send_logs(batch):
                total_sent += len(batch)
                
            # Rate limiting - wait between batches
            if i + batch_size < len(logs):
                print("   ⏳ Waiting 2 seconds before next batch...")
                time.sleep(2)
        
        print("\n" + "=" * 60)
        print(f"✅ COMPLETE: Sent {total_sent} out of {len(logs)} log entries")
        print("=" * 60)
        print("\n📋 Next Steps:")
        print("   1. Wait 5-10 minutes for data to appear in Azure")
        print("   2. Go to Log Analytics Workspace → Logs")
        print("   3. Run query: StudentLoginAttempts_CL | take 10")
        
    except FileNotFoundError:
        print("❌ ERROR: config.json file not found!")
        print("   Please create config.json with your Azure credentials")
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\n📋 How to fix:")
        print("   1. Go to Azure Portal")
        print("   2. Navigate to your Log Analytics workspace")
        print("   3. Settings → Agents → Log Analytics agent instructions")
        print("   4. Copy WORKSPACE ID and PRIMARY KEY exactly")
        print("   5. Update config.json with these values")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()