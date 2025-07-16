#!/bin/bash

echo "🔐 Google Cloud Authentication Fix Script"
echo "================================"

cd /home/liuwei/AI_2.0/malaysia-ai-backend

# Check .env file
if [ ! -f ".env" ]; then
    echo "❌ .env file not found, creating from template..."
    if [ -f ".env.template" ]; then
        cp .env.template .env
        echo "✅ .env file created"
    else
        echo "❌ .env.template file not found"
        exit 1
    fi
fi

echo "✅ .env file found"
echo ""

# Display current configuration
echo "📋 Current .env configuration:"
grep -E "^(GOOGLE_|VERTEX_)" .env || echo "   (No Google-related configuration found)"
echo ""

# Check authentication configuration
echo "🔍 Checking authentication configuration..."

HAS_FILE_AUTH=false
HAS_JSON_AUTH=false

if grep -q "^GOOGLE_APPLICATION_CREDENTIALS=" .env; then
    CREDS_FILE=$(grep "^GOOGLE_APPLICATION_CREDENTIALS=" .env | cut -d'=' -f2)
    if [ -f "$CREDS_FILE" ]; then
        echo "✅ Found service account file: $CREDS_FILE"
        HAS_FILE_AUTH=true
    else
        echo "❌ Service account file does not exist: $CREDS_FILE"
    fi
fi

if grep -q "^GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON=" .env; then
    echo "✅ Found service account JSON configuration"
    HAS_JSON_AUTH=true
fi

if [ "$HAS_FILE_AUTH" = false ] && [ "$HAS_JSON_AUTH" = false ]; then
    echo "❌ No valid authentication configuration found"
    echo ""
    echo "📝 Please choose authentication method:"
    echo "1. Use service account JSON file (recommended)"
    echo "2. Use JSON string"
    echo "3. Show configuration examples"
    
    read -p "Please choose (1-3): " auth_choice
    
    case $auth_choice in
        1)
            echo ""
            echo "📂 Please place service account JSON file in a secure location:"
            echo "   mkdir -p /home/liuwei/.gcp"
            echo "   mv /path/to/your-service-account.json /home/liuwei/.gcp/service-account.json"
            echo "   chmod 600 /home/liuwei/.gcp/service-account.json"
            echo ""
            echo "Then add to .env file:"
            echo "   GOOGLE_APPLICATION_CREDENTIALS=/home/liuwei/.gcp/service-account.json"
            ;;
        2)
            echo ""
            echo "📝 Add complete JSON string to .env file:"
            echo "   GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON={...complete JSON content...}"
            ;;
        3)
            echo ""
            echo "📋 .env file configuration example:"
            echo ""
            cat << 'EOL'
# Google Cloud configuration
GOOGLE_CLOUD_PROJECT=bright-coyote-463315-q8
GOOGLE_CLOUD_LOCATION=us-west1
VERTEX_AI_ENDPOINT=projects/bright-coyote-463315-q8/locations/us-west1/endpoints/YOUR_ENDPOINT_ID

# Authentication method 1: Use file path
GOOGLE_APPLICATION_CREDENTIALS=/home/liuwei/.gcp/service-account.json

# Authentication method 2: Use JSON string (choose one)
# GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON={"type":"service_account",...}

# Image search (optional)
UNSPLASH_ACCESS_KEY=your_unsplash_key_here

# Server configuration
PORT=8000
EOL
            ;;
    esac
    echo ""
    echo "⚠️  After configuration, please re-run this script to verify"
    exit 1
fi

echo ""
echo "🧪 Testing authentication configuration..."

# Test Python imports and basic configuration
python3 << 'EOF'
import os
import sys
import json

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Successfully loaded .env file")
except ImportError:
    print("❌ python-dotenv not installed, please run: pip install python-dotenv")
    sys.exit(1)

# Check project configuration
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION") 
endpoint = os.getenv("VERTEX_AI_ENDPOINT")

print(f"📋 Project ID: {project_id}")
print(f"📍 Location: {location}")
print(f"🎯 Endpoint: {endpoint}")

# 检查认证
creds_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
creds_json = os.getenv("GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON")

if creds_file:
    try:
        with open(creds_file, 'r') as f:
            data = json.load(f)
        print(f"✅ Service account file valid")
        print(f"📧 Service account: {data.get('client_email', 'unknown')}")
        print(f"🏗️ Project: {data.get('project_id', 'unknown')}")
    except Exception as e:
        print(f"❌ Service account file error: {e}")
        
elif creds_json:
    try:
        data = json.loads(creds_json)
        print(f"✅ Service account JSON valid")
        print(f"📧 Service account: {data.get('client_email', 'unknown')}")
        print(f"🏗️ Project: {data.get('project_id', 'unknown')}")
    except Exception as e:
        print(f"❌ Service account JSON error: {e}")
else:
    print("❌ Authentication configuration not found")
EOF

echo ""
echo "🚀 Next steps:"
echo "1. Ensure authentication configuration is correct"
echo "2. Restart backend server:"
echo "   cd /home/liuwei/AI_2.0/malaysia-ai-backend"
echo "   python3 api_server_genai.py"
echo ""
echo "✅ Success startup indicators:"
echo "   '✅ Google Gen AI client initialized successfully'"
echo "   '✅ Backend initialization complete'"