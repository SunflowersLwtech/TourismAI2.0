# 本地测试指南

## 1. 环境准备

### 1.1 创建本地环境变量文件

在 `malaysia-ai-backend/` 目录下创建 `.env` 文件：

```bash
cd malaysia-ai-backend
touch .env
```

### 1.2 配置环境变量

在 `.env` 文件中添加以下内容：

```env
# 你的 Google Cloud 项目信息
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=us-west1

# 你的微调模型端点 (替换为你的实际端点)
VERTEX_AI_ENDPOINT=projects/your_project_id/locations/us-west1/endpoints/your_endpoint_id

# Google Cloud 服务账号 JSON 文件路径
GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON=/path/to/your/service-account-key.json

# Gemini API Key (备用)
GEMINI_API_KEY=your_gemini_api_key_here

# 本地服务器配置
PORT=8000
PYTHON_VERSION=3.11.5
```

### 1.3 安装依赖

```bash
# 确保你在 malaysia-ai-backend 目录
cd malaysia-ai-backend

# 安装 Python 依赖
pip install -r requirements.txt

# 如果你使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或者
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

## 2. 启动本地服务器

### 2.1 启动后端 API 服务器

```bash
cd malaysia-ai-backend
python api_server_genai.py
```

你应该看到类似的输出：
```
🚀 Starting AI Chat Backend with Google Gen AI SDK...
🔧 Project: your_project_id
🔧 Location: us-west1
🔧 Endpoint: projects/your_project_id/locations/us-west1/endpoints/your_endpoint_id
✅ Google Gen AI client initialized successfully
✅ Using fine-tuned model endpoint: projects/your_project_id/locations/us-west1/endpoints/your_endpoint_id
✅ Backend initialization complete
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2.2 启动前端 Streamlit 应用

打开新的终端窗口：

```bash
cd malaysia-ai-backend
streamlit run streamlit_app.py
```

你应该看到：
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

## 3. 测试方法

### 3.1 通过 Web 界面测试

1. 打开浏览器访问 `http://localhost:8501`
2. 你会看到 Aiman 聊天界面
3. 点击图像上传按钮（📷）
4. 选择一张图片上传
5. 输入消息或直接发送
6. 查看 Aiman 的图像分析结果

### 3.2 通过 API 直接测试

使用 curl 或 Postman 测试：

```bash
# 测试文本聊天
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好，我想了解马来西亚的美食",
    "temperature": 0.7
  }'

# 测试图像上传
curl -X POST "http://localhost:8000/upload-image" \
  -F "file=@/path/to/your/image.jpg" \
  -F "message=这是什么菜？"
```

## 4. 调试和监控

### 4.1 查看日志

后端服务器会显示详细的日志，关注这些关键信息：

```
🎯 Using fine-tuned Gemini 2.5 Flash model for image analysis
📸 Created image content for fine-tuned model analysis
🤖 Generated image analysis with fine-tuned model: XXX chars
```

### 4.2 常见问题排查

**问题 1: 模型访问失败**
```
❌ Image analysis error: 403 Forbidden
```
解决方案：
- 检查服务账号权限
- 确认模型端点URL正确
- 验证项目ID和位置

**问题 2: 图像处理失败**
```
Error creating image part: Invalid image format
```
解决方案：
- 确认图像格式支持（JPEG, PNG, WebP）
- 检查图像大小（< 10MB）
- 验证图像文件完整性

**问题 3: 认证问题**
```
❌ Failed to setup credentials
```
解决方案：
- 检查服务账号JSON文件路径
- 确认环境变量设置正确
- 验证 Google Cloud 认证

## 5. 测试用例

### 5.1 食物图像测试

准备一些食物图片：
- 中式菜肴（测试推荐马来西亚中式餐厅）
- 东南亚菜肴（测试识别相似马来菜）
- 西式餐点（测试推荐马来西亚西餐）

期望结果：
- 准确识别食物类型
- 推荐相关马来西亚餐厅或菜品
- 保持 Aiman 角色的友好语调

### 5.2 景点图像测试

准备一些景点图片：
- 建筑物（测试推荐马来西亚相似建筑）
- 自然风景（测试推荐马来西亚自然景点）
- 文化场所（测试推荐马来西亚文化体验）

期望结果：
- 识别建筑特色和风格
- 推荐马来西亚相似景点
- 提供实用的旅游建议

### 5.3 文化元素测试

准备一些文化图片：
- 传统服饰
- 节日庆典
- 艺术品

期望结果：
- 识别文化特色
- 关联到马来西亚文化
- 推荐相关体验活动

## 6. 性能监控

### 6.1 响应时间监控

在日志中查找：
```
🤖 Generated image analysis with fine-tuned model: XXX chars
```

正常响应时间应该在 2-10 秒之间。

### 6.2 错误率监控

监控这些错误模式：
- 模型访问失败
- 图像处理错误
- 认证问题

### 6.3 降级机制测试

故意让微调模型失败，测试是否正确降级到备用模型：
- 修改端点URL
- 观察是否使用 `gemini-2.0-flash-exp`
- 确认仍能正常分析图像

## 7. 部署前验证

在部署到生产环境前，确保：

1. ✅ 所有测试用例通过
2. ✅ 微调模型正常工作
3. ✅ 错误处理机制正常
4. ✅ 响应时间可接受
5. ✅ 日志记录完整
6. ✅ 安全配置正确

## 8. 故障排除清单

### 8.1 启动失败

- [ ] 检查 Python 版本（3.11+）
- [ ] 确认所有依赖已安装
- [ ] 验证环境变量设置
- [ ] 检查端口占用情况

### 8.2 图像分析失败

- [ ] 确认模型端点可访问
- [ ] 检查认证配置
- [ ] 验证图像格式支持
- [ ] 查看详细错误日志

### 8.3 性能问题

- [ ] 监控响应时间
- [ ] 检查网络连接
- [ ] 确认模型配置优化
- [ ] 考虑调整参数设置