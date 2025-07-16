#!/bin/bash

# 🚀 Malaysia Tourism AI - Render部署脚本
# 使用说明：chmod +x deploy_to_render.sh && ./deploy_to_render.sh

echo "🇲🇾 Malaysia Tourism AI - Render部署助手"
echo "=========================================="

# 检查是否有git
if ! command -v git &> /dev/null; then
    echo "❌ 错误：未安装git"
    exit 1
fi

# 检查是否在git仓库中
if [ ! -d .git ]; then
    echo "❌ 错误：不在git仓库中"
    exit 1
fi

echo "📋 部署前检查..."

# 1. 检查重要文件
echo "1️⃣ 检查项目文件..."
if [ ! -f "malaysia-ai-backend/api_server_genai.py" ]; then
    echo "❌ 缺少后端文件：malaysia-ai-backend/api_server_genai.py"
    exit 1
fi

if [ ! -f "malaysia-ai-backend/requirements.txt" ]; then
    echo "❌ 缺少后端依赖：malaysia-ai-backend/requirements.txt"
    exit 1
fi

if [ ! -f "malaysia-ai-frontend/streamlit_app.py" ]; then
    echo "❌ 缺少前端文件：malaysia-ai-frontend/streamlit_app.py"
    exit 1
fi

echo "✅ 项目文件检查完成"

# 2. 检查环境变量文件
echo "2️⃣ 检查环境变量..."
if [ ! -f "malaysia-ai-backend/.env.production" ]; then
    echo "❌ 缺少生产环境配置：malaysia-ai-backend/.env.production"
    echo "请确保已经创建了包含所有必需环境变量的 .env.production 文件"
    exit 1
fi

echo "✅ 环境变量检查完成"

# 3. 推送到GitHub
echo "3️⃣ 推送代码到GitHub..."
git add .
git commit -m "Prepare for Render deployment - $(date)"
git push origin main

if [ $? -eq 0 ]; then
    echo "✅ 代码推送成功"
else
    echo "❌ 代码推送失败"
    exit 1
fi

echo ""
echo "🎉 部署准备完成！"
echo ""
echo "📋 接下来的步骤："
echo "1. 访问 https://render.com"
echo "2. 使用GitHub账户登录"
echo "3. 创建新的Web Service"
echo "4. 连接到仓库：SunflowersLwtech/AI_2.0"
echo ""
echo "🔧 后端部署配置："
echo "   - Name: malaysia-ai-backend"
echo "   - Language: Python"
echo "   - Branch: main"
echo "   - Root Directory: malaysia-ai-backend"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: python api_server_genai.py"
echo ""
echo "🎨 前端部署配置："
echo "   - Name: malaysia-ai-frontend"
echo "   - Language: Python"
echo "   - Branch: main"
echo "   - Root Directory: malaysia-ai-frontend"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: streamlit run streamlit_app.py --server.port \$PORT --server.address 0.0.0.0 --server.headless true --server.enableCORS false"
echo ""
echo "📖 详细教程请查看：RENDER_DEPLOYMENT_TUTORIAL.md"
echo ""
echo "🌟 环境变量配置请参考：malaysia-ai-backend/.env.production"
echo ""
echo "部署成功后，你的应用将在以下URL可用："
echo "- 后端：https://malaysia-ai-backend.onrender.com"
echo "- 前端：https://malaysia-ai-frontend.onrender.com"
echo ""
echo "🚀 祝你部署顺利！"