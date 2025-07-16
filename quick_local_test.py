#!/usr/bin/env python3
"""
🚀 马来西亚旅游AI系统 - 快速本地测试脚本
快速验证修复后的功能是否正常工作
"""

import requests
import json
import time
import os
from typing import Dict, Any

# 测试配置
BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def print_header(title: str):
    """打印测试标题"""
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)

def print_result(success: bool, message: str):
    """打印测试结果"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")

def test_backend_health():
    """测试后端健康状态"""
    print_header("后端健康检查")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "后端服务器运行正常")
            print(f"   📊 状态: {data.get('status', 'unknown')}")
            print(f"   🤖 模型端点: {data.get('model_endpoint', 'unknown')}")
            print(f"   🌍 环境: {data.get('environment', 'unknown')}")
            return True
        else:
            print_result(False, f"后端响应异常: {response.status_code}")
            return False
            
    except requests.RequestException as e:
        print_result(False, f"无法连接到后端: {e}")
        print("💡 请确保后端服务器正在运行:")
        print("   cd malaysia-ai-backend && python api_server_genai.py")
        return False

def test_text_chat():
    """测试文本聊天功能"""
    print_header("文本聊天功能测试")
    
    test_messages = [
        "你好，我想了解马来西亚旅游",
        "推荐吉隆坡的美食",
        "马来西亚有什么著名景点？"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n🔍 测试 {i}/3: {message}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                json={
                    "message": message,
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                reply = data.get("response", "")
                model_used = data.get("model_used", "unknown")
                contains_images = data.get("contains_images", False)
                contains_actions = data.get("contains_actions", False)
                search_queries = data.get("search_image_queries", [])
                action_items = data.get("action_items", [])
                
                print_result(True, f"聊天响应正常 (模型: {model_used})")
                print(f"   💬 回复长度: {len(reply)} 字符")
                print(f"   🖼️ 包含图像搜索: {contains_images} ({len(search_queries)} 个查询)")
                print(f"   🎯 包含动作指令: {contains_actions} ({len(action_items)} 个动作)")
                
                if search_queries:
                    print(f"   🔍 搜索查询: {search_queries}")
                
                if action_items:
                    print(f"   🎯 动作项目: {action_items}")
                
                # 显示回复预览
                preview = reply[:100] + "..." if len(reply) > 100 else reply
                print(f"   📝 回复预览: {preview}")
                
            else:
                print_result(False, f"聊天请求失败: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   ❌ 错误详情: {error_data}")
                except:
                    print(f"   ❌ 错误详情: {response.text}")
                
        except requests.RequestException as e:
            print_result(False, f"聊天请求异常: {e}")
        
        # 避免请求过于频繁
        time.sleep(1)

def test_image_search():
    """测试图像搜索功能"""
    print_header("图像搜索功能测试")
    
    test_queries = [
        "Nasi Lemak Malaysian food",
        "Kuala Lumpur skyline",
        "Penang street food"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 测试 {i}/3: {query}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/image-search",
                json={
                    "query": query,
                    "max_results": 3
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                images = data.get("images", [])
                
                if images:
                    print_result(True, f"找到 {len(images)} 张图片")
                    for j, image in enumerate(images[:2], 1):
                        print(f"   📸 图片 {j}: {image.get('title', 'No title')}")
                        print(f"      🔗 URL: {image.get('url', 'No URL')}")
                else:
                    print_result(False, "未找到图片")
                    
            else:
                print_result(False, f"图像搜索失败: {response.status_code}")
                
        except requests.RequestException as e:
            print_result(False, f"图像搜索异常: {e}")

def test_frontend_connection():
    """测试前端连接"""
    print_header("前端连接测试")
    
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        
        if response.status_code == 200:
            print_result(True, "前端Streamlit应用运行正常")
            print("   🌐 访问地址: http://localhost:8501")
        else:
            print_result(False, f"前端响应异常: {response.status_code}")
            
    except requests.RequestException as e:
        print_result(False, f"无法连接到前端: {e}")
        print("💡 请确保前端应用正在运行:")
        print("   cd malaysia-ai-backend && streamlit run streamlit_app.py")

def generate_test_report():
    """生成测试报告"""
    print_header("测试报告生成")
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tests_run": 4,
        "system_status": "需要手动检查各项测试结果"
    }
    
    try:
        with open("/home/liuwei/AI_2.0/test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print_result(True, "测试报告已生成: test_report.json")
    except Exception as e:
        print_result(False, f"生成报告失败: {e}")

def main():
    """主测试函数"""
    print("🇲🇾 马来西亚旅游AI系统 - 本地测试")
    print("=" * 60)
    print("📋 测试内容:")
    print("   1. 后端健康检查")
    print("   2. 文本聊天功能")
    print("   3. 图像搜索功能")
    print("   4. 前端连接测试")
    print()
    
    # 运行测试
    backend_ok = test_backend_health()
    
    if backend_ok:
        test_text_chat()
        test_image_search()
    else:
        print("\n⚠️  后端不可用，跳过功能测试")
    
    test_frontend_connection()
    generate_test_report()
    
    print_header("测试完成")
    print("📊 测试总结:")
    print("   - 检查上述各项测试结果")
    print("   - 如有问题，查看详细错误信息")
    print("   - 确保 .env 配置正确")
    print("   - 确保服务账号权限正确")
    print()
    print("🎯 下一步:")
    print("   1. 打开浏览器访问 http://localhost:8501")
    print("   2. 测试聊天功能")
    print("   3. 测试图像上传功能")
    print("   4. 查看图像搜索结果")

if __name__ == "__main__":
    main()