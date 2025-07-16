#!/bin/bash

# 🇲🇾 马来西亚旅游AI系统 - 快速启动脚本

echo "🚀 启动马来西亚旅游AI系统"
echo "================================="

# 检查目录
if [ ! -d "malaysia-ai-backend" ]; then
    echo "❌ 错误: 请在 AI_2.0 目录运行此脚本"
    exit 1
fi

cd malaysia-ai-backend

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 文件"
    echo "📋 请创建 .env 文件并配置以下变量:"
    echo "   GOOGLE_CLOUD_PROJECT=your-project-id"
    echo "   VERTEX_AI_ENDPOINT=your-endpoint-url"
    echo "   GOOGLE_APPLICATION_CREDENTIALS=path-to-service-account.json"
    echo ""
    echo "📖 详细说明请查看: LOCAL_TESTING_COMPLETE_GUIDE.md"
    exit 1
fi

echo "✅ 找到配置文件"

# 检查Python环境
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "🐍 Python 版本: $python_version"

# 安装依赖
echo "📦 安装后端依赖..."
pip3 install -r requirements.txt

echo "📦 安装前端依赖..."
pip3 install -r streamlit_requirements.txt

echo ""
echo "🎯 选择启动方式:"
echo "1. 只启动后端 (API服务器)"
echo "2. 只启动前端 (Streamlit应用)"
echo "3. 运行测试脚本"
echo "4. 显示启动命令 (手动启动)"

read -p "请选择 (1-4): " choice

case $choice in
    1)
        echo "🚀 启动后端API服务器..."
        python3 api_server_genai.py
        ;;
    2)
        echo "🚀 启动前端Streamlit应用..."
        streamlit run streamlit_app.py --server.port 8501
        ;;
    3)
        echo "🧪 运行测试脚本..."
        cd ..
        python3 quick_local_test.py
        ;;
    4)
        echo "📋 手动启动命令:"
        echo ""
        echo "启动后端 (终端1):"
        echo "  cd malaysia-ai-backend"
        echo "  python3 api_server_genai.py"
        echo ""
        echo "启动前端 (终端2):"
        echo "  cd malaysia-ai-backend"
        echo "  streamlit run streamlit_app.py"
        echo ""
        echo "运行测试 (终端3):"
        echo "  python3 quick_local_test.py"
        echo ""
        echo "访问地址:"
        echo "  前端界面: http://localhost:8501"
        echo "  API文档: http://localhost:8000/docs"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac