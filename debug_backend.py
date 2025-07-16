#!/usr/bin/env python3
"""
Debug backend startup issues
"""

import os
import sys
import traceback

# Change to backend directory
os.chdir('/home/liuwei/AI_2.0/malaysia-ai-backend')

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded")
except Exception as e:
    print(f"❌ Failed to load environment: {e}")
    sys.exit(1)

# Test imports
print("\n🔍 Testing imports...")
try:
    from fastapi import FastAPI
    print("✅ FastAPI imported")
except Exception as e:
    print(f"❌ FastAPI import failed: {e}")

try:
    from google import genai
    print("✅ Google GenAI imported")
except Exception as e:
    print(f"❌ Google GenAI import failed: {e}")

try:
    from google.oauth2 import service_account
    print("✅ Service account imported")
except Exception as e:
    print(f"❌ Service account import failed: {e}")

# Test credential setup
print("\n🔧 Testing credential setup...")
try:
    import json
    from google.oauth2 import service_account
    
    google_creds_json = os.getenv("GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON")
    if google_creds_json:
        creds_info = json.loads(google_creds_json)
        
        VERTEX_AI_SCOPES = [
            'https://www.googleapis.com/auth/cloud-platform',
            'https://www.googleapis.com/auth/cloud-platform.read-only',
            'https://www.googleapis.com/auth/devstorage.full_control',
            'https://www.googleapis.com/auth/devstorage.read_only',
            'https://www.googleapis.com/auth/devstorage.read_write'
        ]
        
        credentials = service_account.Credentials.from_service_account_info(
            creds_info,
            scopes=VERTEX_AI_SCOPES
        )
        print("✅ Credentials created successfully")
        
        # Test GenAI client
        client = genai.Client(
            vertexai=True,
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION"),
            credentials=credentials
        )
        print("✅ GenAI client created successfully")
        
    else:
        print("❌ No GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON found")
        
except Exception as e:
    print(f"❌ Credential setup failed: {e}")
    traceback.print_exc()

# Test server startup
print("\n🚀 Testing server startup...")
try:
    # Import the main module
    import api_server_genai
    print("✅ Main module imported")
    
    # Check if app is created
    if hasattr(api_server_genai, 'app'):
        print("✅ FastAPI app created")
    else:
        print("❌ FastAPI app not found")
        
except Exception as e:
    print(f"❌ Server startup test failed: {e}")
    traceback.print_exc()

print("\n📋 Summary:")
print("If all tests pass, try running:")
print("  python3 api_server_genai.py")
print("And let it run in the background, then test with:")
print("  curl http://localhost:8000/health")