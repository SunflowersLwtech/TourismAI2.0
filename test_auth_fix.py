#!/usr/bin/env python3
"""
Test authentication fix effectiveness
"""

import os
import sys
import json

# Change to correct directory
backend_dir = '/home/liuwei/AI_2.0/malaysia-ai-backend'
os.chdir(backend_dir)

# Load environment variables
try:
    from dotenv import load_dotenv
    
    # Explicitly specify .env file path
    env_file = os.path.join(backend_dir, '.env')
    if os.path.exists(env_file):
        result = load_dotenv(env_file)
        print(f"✅ Successfully loaded .env file: {env_file}")
        print(f"📁 Load result: {result}")
    else:
        print(f"❌ .env file does not exist: {env_file}")
        sys.exit(1)
except ImportError:
    print("❌ Need to install python-dotenv: pip install python-dotenv")
    sys.exit(1)

print("\n🔍 Checking environment variables:")
print("=" * 50)

# Check basic configuration
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION") 
endpoint = os.getenv("VERTEX_AI_ENDPOINT")

print(f"📋 Project ID: {project_id}")
print(f"📍 Location: {location}")
print(f"🎯 Endpoint: {endpoint}")

# Check authentication configuration
print("\n🔐 Checking authentication configuration:")
print("=" * 50)

creds_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
creds_json = os.getenv("GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON")

if creds_json:
    try:
        data = json.loads(creds_json)
        print(f"✅ Found GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON")
        print(f"📧 Service account: {data.get('client_email', 'unknown')}")
        print(f"🏗️ Project: {data.get('project_id', 'unknown')}")
        print(f"🔑 Private key ID: {data.get('private_key_id', 'unknown')[:8]}...")
    except Exception as e:
        print(f"❌ GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON format error: {e}")
        
elif creds_file:
    if os.path.exists(creds_file):
        try:
            with open(creds_file, 'r') as f:
                data = json.load(f)
            print(f"✅ Found service account file: {creds_file}")
            print(f"📧 Service account: {data.get('client_email', 'unknown')}")
            print(f"🏗️ Project: {data.get('project_id', 'unknown')}")
        except Exception as e:
            print(f"❌ Service account file error: {e}")
    else:
        print(f"❌ Service account file not found: {creds_file}")
else:
    print("❌ No authentication configuration found")

# Test imports
print("\n🧪 Testing Python module imports:")
print("=" * 50)

try:
    from google.oauth2 import service_account
    print("✅ google.oauth2.service_account - OK")
except ImportError as e:
    print(f"❌ google.oauth2.service_account - {e}")

try:
    from google import genai
    print("✅ google.genai - OK")
except ImportError as e:
    print(f"❌ google.genai - {e}")

# Test authentication initialization
print("\n🔧 Testing authentication initialization:")
print("=" * 50)

try:
    if creds_json:
        # Test JSON string method
        data = json.loads(creds_json)
        
        # Simulate credential creation
        from google.oauth2 import service_account
        VERTEX_AI_SCOPES = [
            'https://www.googleapis.com/auth/cloud-platform',
            'https://www.googleapis.com/auth/cloud-platform.read-only'
        ]
        
        credentials = service_account.Credentials.from_service_account_info(
            data,
            scopes=VERTEX_AI_SCOPES
        )
        print("✅ Authentication credentials created successfully")
        print(f"🎯 Service account email: {credentials.service_account_email}")
        print(f"🔧 Scope count: {len(VERTEX_AI_SCOPES)} scopes")
        
    elif creds_file and os.path.exists(creds_file):
        # Test file method
        from google.oauth2 import service_account
        credentials = service_account.Credentials.from_service_account_file(
            creds_file,
            scopes=VERTEX_AI_SCOPES
        )
        print("✅ Authentication credentials created from file successfully")
        
    else:
        print("❌ Cannot create authentication credentials - missing configuration")
        
except Exception as e:
    print(f"❌ Authentication credential creation failed: {e}")

print("\n🚀 Recommended next steps:")
print("=" * 50)
print("1. If all checks pass, restart the backend:")
print("   cd /home/liuwei/AI_2.0/malaysia-ai-backend")
print("   python3 api_server_genai.py")
print("")
print("2. Look for these success messages in the startup log:")
print("   '🔍 Found GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON environment variable'")
print("   '🔐 Service account credentials loaded from environment JSON'")
print("   '✅ Google Gen AI client initialized successfully'")
print("")
print("3. If there are still issues, please provide the complete error log")