# 🚀 Malaysia Tourism AI - Render部署完整教程

## 📋 目录
1. [前置准备](#前置准备)
2. [后端部署](#后端部署)
3. [前端部署](#前端部署)
4. [环境变量配置](#环境变量配置)
5. [部署验证](#部署验证)
6. [故障排除](#故障排除)

---

## 🔧 前置准备

### 1. 注册Render账户
1. 访问 [render.com](https://render.com)
2. 使用GitHub账户登录
3. 确保已经将代码推送到GitHub仓库

### 2. GitHub仓库准备
- 仓库地址：`https://github.com/SunflowersLwtech/AI_2.0.git`
- 确保所有文件已经推送到main分支

---

## 🖥️ 后端部署

### 第1步：创建新的Web Service

1. 在Render Dashboard点击 **"New +"**
2. 选择 **"Web Service"**
3. 连接GitHub仓库：`SunflowersLwtech/AI_2.0`

### 第2步：配置基本设置

```yaml
Name: malaysia-ai-backend
Language: Python
Branch: main
Root Directory: malaysia-ai-backend
```

### 第3步：配置构建和启动命令

```bash
# Build Command
pip install -r requirements.txt

# Start Command
python api_server_genai.py
```

### 第4步：配置环境变量

在 **Environment Variables** 部分添加以下变量：

```env
# Google Cloud配置
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-west1
VERTEX_AI_ENDPOINT=projects/your-project-id/locations/us-west1/endpoints/your-endpoint-id

# API密钥
GEMINI_API_KEY=your-gemini-api-key
UNSPLASH_ACCESS_KEY=your-unsplash-access-key

# 服务账户JSON (重要!)
GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"your-project-id","private_key_id":"your-private-key-id","private_key":"-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n","client_email":"your-service-account@your-project.iam.gserviceaccount.com","client_id":"your-client-id","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com","universe_domain":"googleapis.com"}

# 服务器配置
PORT=8000
PYTHON_VERSION=3.11.5
```

### 第5步：部署后端

1. 点击 **"Create Web Service"**
2. 等待部署完成（约5-10分钟）
3. 记录后端URL，格式为：`https://malaysia-ai-backend.onrender.com`

---

## 🎨 前端部署

### 第1步：创建前端Web Service

1. 在Render Dashboard点击 **"New +"**
2. 选择 **"Web Service"**
3. 连接同一个GitHub仓库：`SunflowersLwtech/AI_2.0`

### 第2步：配置前端设置

```yaml
Name: malaysia-ai-frontend
Language: Python
Branch: main
Root Directory: malaysia-ai-frontend
```

### 第3步：配置前端构建和启动命令

```bash
# Build Command
pip install -r requirements.txt

# Start Command
streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true --server.enableCORS false
```

### 第4步：配置前端环境变量

```env
# 后端API URL (替换为你的后端URL)
API_BASE_URL=https://malaysia-ai-backend.onrender.com
```

### 第5步：部署前端

1. 点击 **"Create Web Service"**
2. 等待部署完成
3. 记录前端URL，格式为：`https://malaysia-ai-frontend.onrender.com`

---

## 🔧 环境变量配置详解

### 关键环境变量说明

| 变量名 | 描述 | 必需 |
|--------|------|------|
| `GOOGLE_CLOUD_PROJECT` | Google Cloud项目ID | ✅ |
| `GOOGLE_CLOUD_LOCATION` | Vertex AI区域 | ✅ |
| `VERTEX_AI_ENDPOINT` | 微调模型端点 | ✅ |
| `GEMINI_API_KEY` | Gemini API密钥 | ✅ |
| `GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON` | 服务账户JSON | ✅ |
| `UNSPLASH_ACCESS_KEY` | 图片搜索API密钥 | ⚠️ |
| `PORT` | 服务器端口 | ✅ |

### 🚨 重要注意事项

1. **JSON格式**：`GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON`必须是一行，所有换行符替换为`\n`
2. **无引号**：在Render环境变量中不要添加额外的引号
3. **敏感信息**：这些是生产环境密钥，请妥善保管

---

## ✅ 部署验证

### 验证后端部署

1. 访问：`https://malaysia-ai-backend.onrender.com/health`
2. 应该看到：
```json
{
  "status": "healthy",
  "message": "AI Chat Backend (Google Gen AI SDK) is running",
  "model_endpoint": "projects/bright-coyote-463315-q8/locations/us-west1/endpoints/1393226367927058432",
  "backend_version": "2.0.0",
  "environment": "production"
}
```

### 验证前端部署

1. 访问：`https://malaysia-ai-frontend.onrender.com`
2. 应该看到Aiman聊天界面
3. 尝试发送测试消息

### 测试完整功能

1. **文本聊天**：发送"Hello, tell me about Kuala Lumpur"
2. **图片上传**：上传马来西亚美食图片
3. **预订链接**：询问"I want to visit Petronas Twin Towers"

---

## 🔍 故障排除

### 常见问题及解决方案

#### 1. 后端部署失败

**症状**：构建失败或启动失败
**解决方案**：
- 检查`requirements.txt`是否完整
- 确认环境变量格式正确
- 查看Render日志中的错误信息

#### 2. 认证失败

**症状**：Google Cloud API调用失败
**解决方案**：
- 检查`GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON`格式
- 确认服务账户有Vertex AI权限
- 验证项目ID和端点URL

#### 3. 前端无法连接后端

**症状**：前端显示连接错误
**解决方案**：
- 确认后端URL在前端环境变量中正确设置
- 检查后端健康检查端点是否可访问
- 验证CORS设置

#### 4. 图片搜索失败

**症状**：图片搜索返回空结果
**解决方案**：
- 检查`UNSPLASH_ACCESS_KEY`是否有效
- 验证Unsplash API配额
- 查看后端日志中的API调用错误

#### 5. 冷启动问题

**症状**：首次访问需要等待很长时间
**解决方案**：
- 这是Render免费版的正常行为
- 可以使用外部监控服务定期ping保持活跃
- 考虑升级到付费版本

---

## 📊 部署后的URL

部署成功后，你将获得以下URL：

- **后端API**：`https://malaysia-ai-backend.onrender.com`
- **前端界面**：`https://malaysia-ai-frontend.onrender.com`
- **健康检查**：`https://malaysia-ai-backend.onrender.com/health`

---

## 🎯 下一步

1. **自定义域名**：在Render中配置自定义域名
2. **监控设置**：使用Render监控面板跟踪性能
3. **日志分析**：定期检查应用日志
4. **性能优化**：根据使用情况调整资源配置

---

## 📞 技术支持

如果遇到问题，请：
1. 检查Render部署日志
2. 验证环境变量配置
3. 测试本地开发环境
4. 查看GitHub Issues或创建新问题

---

**部署完成！🎉 你的马来西亚旅游AI现已上线！**