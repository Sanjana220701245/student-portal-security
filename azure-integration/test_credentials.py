import json
import base64

def validate_config():
    print("Testing Azure credentials...")
    print("=" * 60)
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        workspace_id = config['workspace_id'].strip()
        shared_key = config['shared_key'].strip()
        
        # Test Workspace ID
        print(f"Workspace ID: {workspace_id}")
        print(f"   Length: {len(workspace_id)} characters")
        
        if len(workspace_id) == 36:
            print("   ✅ Workspace ID format looks correct")
        else:
            print("   ❌ Workspace ID should be 36 characters")
            return False
        
        # Test Shared Key
        print(f"\nShared Key preview: {shared_key[:20]}...{shared_key[-10:]}")
        print(f"   Length: {len(shared_key)} characters")
        
        # Try to decode
        try:
            decoded = base64.b64decode(shared_key)
            print(f"   ✅ Shared Key is valid base64 ({len(decoded)} bytes)")
            print("\n✅ Configuration is valid! You can run log_sender.py now")
            return True
        except Exception as e:
            print(f"   ❌ Shared Key is not valid base64: {e}")
            print("\n💡 How to fix:")
            print("   1. Go back to Azure Portal")
            print("   2. Log Analytics workspace → Agents")
            print("   3. Use the COPY button (don't manually select)")
            print("   4. Paste directly into config.json")
            return False
            
    except FileNotFoundError:
        print("❌ config.json not found!")
        return False
    except json.JSONDecodeError:
        print("❌ config.json is not valid JSON!")
        return False

if __name__ == "__main__":
    validate_config()