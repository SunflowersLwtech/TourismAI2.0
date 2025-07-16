# 🇲🇾 马来西亚旅游AI系统 - 本地测试完整指南

## 📋 测试前准备清单

### 1. 环境要求
- ✅ Python 3.11+
- ✅ pip (Python 包管理器)
- ✅ Google Cloud 服务账号 (有 Vertex AI 权限)
- ✅ 您的微调 Gemini 2.5 Flash 模型端点

### 2. 创建环境配置

在 `malaysia-ai-backend` 目录下创建 `.env` 文件：

```bash
cd /home/liuwei/AI_2.0/malaysia-ai-backend
touch .env
```

在 `.env` 文件中添加以下配置：

```env
# 🔧 Google Cloud & Vertex AI 配置 (必需)
GOOGLE_CLOUD_PROJECT=bright-coyote-463315-q8
GOOGLE_CLOUD_LOCATION=us-west1
VERTEX_AI_ENDPOINT=projects/bright-coyote-463315-q8/locations/us-west1/endpoints/6528596580524621824

# 🔐 认证配置 (二选一)
# 方式1: JSON 文件路径
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json

# 方式2: JSON 字符串 (复制整个 JSON 内容)
# GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON={"type":"service_account",...}

# 🖼️ 图像搜索 (可选)
UNSPLASH_ACCESS_KEY=your_unsplash_access_key_here

# 🚀 服务器配置
PORT=8000
```

## 🚀 启动系统 (三种方式)

### 方式1: 使用自动化脚本 (推荐)
```bash
cd /home/liuwei/AI_2.0
./start_local_test.sh
```
选择选项 5 (全部启动)

### 方式2: 手动启动 (分步骤)

#### 第一步：启动后端API服务器
```bash
# 终端1 - 后端
cd /home/liuwei/AI_2.0/malaysia-ai-backend
pip install -r requirements.txt
python api_server_genai.py
```

看到这个输出说明后端启动成功：
```
🚀 Starting AI Chat Backend with Google Gen AI SDK...
🔧 Project: bright-coyote-463315-q8
🔧 Location: us-west1
🔧 Endpoint: projects/.../endpoints/6528596580524621824
✅ Google Gen AI client initialized successfully
✅ Backend initialization complete
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### 第二步：启动前端Streamlit应用
```bash
# 终端2 - 前端
cd /home/liuwei/AI_2.0/malaysia-ai-backend
pip install -r streamlit_requirements.txt
streamlit run streamlit_app.py
```

看到这个输出说明前端启动成功：
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### 方式3: 使用测试脚本验证
```bash
cd /home/liuwei/AI_2.0
python test_image_analysis.py
```

## 🧪 测试功能清单

### 1. 基础连接测试
1. 打开浏览器访问 `http://localhost:8501`
2. 检查左侧边栏显示 "✅ Backend: Connected"
3. 确认模型信息显示正确

### 2. 文本聊天测试
**测试用例1: 基础问候**
```
输入: 你好，我想了解马来西亚旅游
期望: Aiman 用马来语问候，询问旅行偏好
```

**测试用例2: 具体询问**
```
输入: 推荐吉隆坡的美食
期望: 详细美食推荐 + [SEARCH_IMAGE: "query"] 指令
```

### 3. 图像上传测试

**测试用例1: 食物图片**
1. 点击 📎 按钮上传食物图片
2. 输入："这是什么菜？推荐马来西亚类似美食"
3. 期望：
   - 识别食物类型
   - 推荐马来西亚相似菜品
   - 显示相关图片搜索结果

**测试用例2: 风景图片**
1. 上传风景/建筑图片
2. 输入："推荐马来西亚类似的地方"
3. 期望：
   - 分析风景特色
   - 推荐马来西亚相似景点
   - 提供旅游建议

### 4. 图像搜索功能测试
1. 发送包含推荐的消息
2. 查看是否显示 "🖼️ 相关图片" 部分
3. 验证图片是否正确加载

### 5. 动作指令测试
1. 询问具体酒店或活动推荐
2. 查看是否显示 "🎯 推荐行动" 部分
3. 测试动作按钮是否可点击

## 🔧 故障排除

### 问题1: 后端启动失败
**症状**: `❌ Failed to setup credentials`
**解决**:
```bash
# 检查环境变量
echo $GOOGLE_APPLICATION_CREDENTIALS
# 或检查 .env 文件是否正确配置
cat .env
```

### 问题2: 前端无法连接后端
**症状**: "❌ Backend: Disconnected"
**解决**:
1. 确认后端在 8000 端口运行
2. 检查防火墙设置
3. 验证 API_BASE_URL 配置

### 问题3: 图像分析失败
**症状**: "Fine-tuned model is currently unavailable"
**解决**:
1. 验证模型端点 URL
2. 检查服务账号权限
3. 确认项目ID和位置正确

### 问题4: 图像搜索无结果
**症状**: "暂无相关图片"
**解决**:
1. 检查 UNSPLASH_ACCESS_KEY
2. 验证网络连接
3. 查看后端日志

## 📊 健康检查端点

测试各个功能模块：

```bash
# 1. 基础健康检查
curl http://localhost:8000/health

# 2. 文本聊天测试
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}'

# 3. 图像搜索测试
curl -X POST http://localhost:8000/image-search \
  -H "Content-Type: application/json" \
  -d '{"query": "Nasi Lemak", "max_results": 3}'
```

## 🎯 成功指标

系统运行正常的标志：
- ✅ 后端健康检查返回 200
- ✅ 前端显示连接状态正常
- ✅ 文本聊天有正确的 Aiman 回复
- ✅ 图像上传能被正确分析
- ✅ 搜索图片能正常显示
- ✅ 动作卡片能正确渲染

## 🚨 重要提醒

1. **只使用微调模型**: 系统已配置为专门使用您的 Gemini 2.5 Flash 微调模型
2. **网络依赖**: 需要网络连接到 Google Cloud 和 Unsplash API
3. **API 配额**: 注意 Vertex AI 和 Unsplash 的使用配额
4. **调试日志**: 查看终端输出获取详细的调试信息

## 📞 需要帮助？

如果遇到问题，请提供：
1. 错误消息的完整截图
2. 浏览器控制台日志
3. 后端终端输出
4. `.env` 配置 (隐藏敏感信息)

祝您测试顺利！🎉