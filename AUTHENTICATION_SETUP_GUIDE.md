# 🔐 Google Cloud 认证配置完整指南

## 🚨 当前问题分析

从错误信息看：
```
WARNING: Local credential file not found: bright-coyote-463315-q8-59797318b374.json
ERROR: Your default credentials were not found
ERROR: Failed to setup Google Cloud credentials
```

**问题原因**: 系统无法找到Google Cloud认证凭据

## 📋 解决方案 (3种方式)

### 方式1: 使用服务账号JSON文件 (推荐)

#### 步骤1: 获取服务账号JSON文件
1. 访问 [Google Cloud Console](https://console.cloud.google.com)
2. 选择项目: `bright-coyote-463315-q8`
3. 导航到 **IAM & Admin** > **Service Accounts**
4. 找到有 Vertex AI 权限的服务账号
5. 点击 **Keys** > **Add Key** > **Create New Key**
6. 选择 **JSON** 格式下载

#### 步骤2: 配置文件路径
```bash
# 将JSON文件放到安全位置
mkdir -p /home/liuwei/.gcp
mv ~/Downloads/your-service-account-key.json /home/liuwei/.gcp/service-account.json
chmod 600 /home/liuwei/.gcp/service-account.json
```

#### 步骤3: 更新.env文件
```bash
cd /home/liuwei/AI_2.0/malaysia-ai-backend
```

编辑 `.env` 文件：
```env
# Google Cloud 配置
GOOGLE_CLOUD_PROJECT=bright-coyote-463315-q8
GOOGLE_CLOUD_LOCATION=us-west1
VERTEX_AI_ENDPOINT=projects/bright-coyote-463315-q8/locations/us-west1/endpoints/6528596580524621824

# 认证配置 - 使用文件路径
GOOGLE_APPLICATION_CREDENTIALS=/home/liuwei/.gcp/service-account.json

# 图像搜索 (可选)
UNSPLASH_ACCESS_KEY=your_unsplash_key_here

# 服务器配置
PORT=8000
```

### 方式2: 使用JSON字符串 (适用于云部署)

如果您有服务账号的JSON内容，可以直接配置：

```env
# 不使用文件路径，而是直接提供JSON内容
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/file.json  # 注释掉这行

# 使用JSON字符串
GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"bright-coyote-463315-q8","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"...","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"..."}
```

### 方式3: 使用 gcloud CLI (临时测试)

```bash
# 安装 gcloud CLI (如果还没安装)
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# 登录并设置项目
gcloud auth login
gcloud config set project bright-coyote-463315-q8

# 设置应用默认凭据
gcloud auth application-default login
```

## 🧪 验证配置

### 检查1: 环境变量
```bash
cd /home/liuwei/AI_2.0/malaysia-ai-backend
cat .env
```

### 检查2: 文件权限
```bash
# 如果使用文件路径方式
ls -la /home/liuwei/.gcp/service-account.json
```

### 检查3: JSON格式
```bash
# 验证JSON文件格式
python3 -c "
import json
import os
try:
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        with open(os.getenv('GOOGLE_APPLICATION_CREDENTIALS')) as f:
            data = json.load(f)
        print('✅ JSON文件格式正确')
        print(f'📧 服务账号: {data.get(\"client_email\", \"未找到\")}')
        print(f'🆔 项目ID: {data.get(\"project_id\", \"未找到\")}')
    else:
        print('❌ GOOGLE_APPLICATION_CREDENTIALS 未设置')
except Exception as e:
    print(f'❌ JSON文件错误: {e}')
"
```

## 🔧 快速修复脚本

创建并运行这个脚本来快速配置：

```bash
cat > /home/liuwei/AI_2.0/fix_auth.sh << 'EOF'
#!/bin/bash

echo "🔐 Google Cloud 认证修复脚本"
echo "================================"

cd /home/liuwei/AI_2.0/malaysia-ai-backend

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "❌ 未找到.env文件，从模板创建..."
    cp .env.template .env
    echo "📝 请编辑.env文件并配置认证信息"
    exit 1
fi

echo "✅ 找到.env文件"

# 检查认证配置
if grep -q "GOOGLE_APPLICATION_CREDENTIALS=" .env && ! grep -q "^#.*GOOGLE_APPLICATION_CREDENTIALS=" .env; then
    CREDS_FILE=$(grep "GOOGLE_APPLICATION_CREDENTIALS=" .env | cut -d'=' -f2)
    if [ -f "$CREDS_FILE" ]; then
        echo "✅ 找到服务账号文件: $CREDS_FILE"
    else
        echo "❌ 服务账号文件不存在: $CREDS_FILE"
        echo "💡 请确保文件路径正确，或下载新的服务账号JSON文件"
    fi
elif grep -q "GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON=" .env; then
    echo "✅ 找到服务账号JSON配置"
else
    echo "❌ 未找到任何认证配置"
    echo "💡 请在.env文件中配置以下之一:"
    echo "   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"
    echo "   GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON={...json content...}"
fi

echo ""
echo "🚀 配置完成后，重新启动服务器:"
echo "   python3 api_server_genai.py"
EOF

chmod +x /home/liuwei/AI_2.0/fix_auth.sh
```

## 📞 获取帮助

如果仍有问题，请提供：
1. `.env` 文件内容 (隐藏私钥部分)
2. 服务账号的权限设置
3. 是否能访问 Google Cloud Console

## 🎯 下一步行动

1. **立即执行**:
   ```bash
   cd /home/liuwei/AI_2.0
   ./fix_auth.sh
   ```

2. **根据上述方式1配置认证**

3. **重新启动服务器**:
   ```bash
   cd malaysia-ai-backend
   python3 api_server_genai.py
   ```

4. **验证启动成功**:
   看到这个消息表示成功：
   ```
   ✅ Google Gen AI client initialized successfully
   ✅ Backend initialization complete
   ```