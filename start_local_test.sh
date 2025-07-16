#!/bin/bash

# 本地测试启动脚本
# 用于快速启动本地测试环境

set -e

echo "🚀 启动马来西亚旅游 AI 本地测试环境"
echo "=" * 50

# 检查目录
if [ ! -d "malaysia-ai-backend" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

cd malaysia-ai-backend

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 文件"
    if [ -f ".env.local.template" ]; then
        echo "📝 复制模板文件..."
        cp .env.local.template .env
        echo "✅ 已创建 .env 文件，请编辑此文件并填入你的配置"
        echo "📍 需要配置的项目："
        echo "   - GOOGLE_CLOUD_PROJECT"
        echo "   - VERTEX_AI_ENDPOINT"
        echo "   - GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON"
        echo "   - GEMINI_API_KEY"
        echo ""
        echo "配置完成后，请重新运行此脚本"
        exit 1
    else
        echo "❌ 未找到环境变量模板文件"
        exit 1
    fi
fi

# 检查 Python 环境
echo "🐍 检查 Python 环境..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python 版本: $python_version"

# 检查依赖
echo "📦 检查依赖..."
if [ -f "requirements.txt" ]; then
    echo "安装依赖..."
    pip install -r requirements.txt
else
    echo "❌ 未找到 requirements.txt 文件"
    exit 1
fi

# 创建测试图像目录
echo "📁 创建测试目录..."
mkdir -p ../test_images

# 启动选项
echo ""
echo "🎯 选择启动选项:"
echo "1. 启动后端 API 服务器 (端口 8000)"
echo "2. 启动前端 Streamlit 应用 (端口 8501)"
echo "3. 运行测试脚本"
echo "4. 显示配置信息"
echo "5. 全部启动 (推荐)"

read -p "请选择 (1-5): " choice

case $choice in
    1)
        echo "🚀 启动后端 API 服务器..."
        python api_server_genai.py
        ;;
    2)
        echo "🚀 启动前端 Streamlit 应用..."
        streamlit run streamlit_app.py
        ;;
    3)
        echo "🧪 运行测试脚本..."
        cd ..
        python test_image_analysis.py
        ;;
    4)
        echo "📋 显示配置信息..."
        echo "后端服务器: http://localhost:8000"
        echo "前端应用: http://localhost:8501"
        echo "API 文档: http://localhost:8000/docs"
        echo "测试脚本: python test_image_analysis.py"
        ;;
    5)
        echo "🚀 启动全部服务..."
        echo "请在不同终端窗口中运行以下命令:"
        echo ""
        echo "终端 1 (后端):"
        echo "cd malaysia-ai-backend && python api_server_genai.py"
        echo ""
        echo "终端 2 (前端):"
        echo "cd malaysia-ai-backend && streamlit run streamlit_app.py"
        echo ""
        echo "终端 3 (测试):"
        echo "python test_image_analysis.py"
        echo ""
        echo "访问地址:"
        echo "- 前端界面: http://localhost:8501"
        echo "- API 文档: http://localhost:8000/docs"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "✅ 操作完成"