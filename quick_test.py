#!/usr/bin/env python3
"""
快速测试脚本 - 验证本地服务器是否正常运行
"""

import requests
import json

def test_local_server():
    """测试本地服务器"""
    print("🚀 测试本地服务器...")
    
    # 测试后端健康状态
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ 后端服务器 (8000) 运行正常")
        else:
            print(f"❌ 后端服务器响应异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 后端服务器无法连接: {e}")
        print("请确保运行了: python api_server_genai.py")
    
    # 测试前端 (Streamlit 通常不提供 API 端点，只能通过浏览器访问)
    print("📱 前端界面: http://localhost:8501")
    print("📚 API 文档: http://localhost:8000/docs")
    
    # 测试文本聊天
    try:
        chat_data = {
            "message": "你好，测试消息",
            "temperature": 0.7
        }
        response = requests.post("http://localhost:8000/chat", json=chat_data)
        if response.status_code == 200:
            print("✅ 文本聊天功能正常")
        else:
            print(f"❌ 文本聊天功能异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 文本聊天测试失败: {e}")

if __name__ == "__main__":
    test_local_server()