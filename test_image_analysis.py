#!/usr/bin/env python3
"""
图像分析测试脚本
用于测试微调模型的图像分析功能
"""

import requests
import json
import os
import base64
from typing import Dict, Any

# 配置
BASE_URL = "http://localhost:8000"
TEST_IMAGES_DIR = "./test_images"

def test_api_health():
    """测试 API 健康状态"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ API 健康检查: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API 健康检查失败: {e}")
        return False

def test_text_chat():
    """测试文本聊天功能"""
    try:
        payload = {
            "message": "你好，我想了解马来西亚的美食",
            "temperature": 0.7
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 文本聊天测试成功")
            print(f"📝 响应: {result['response'][:100]}...")
            return True
        else:
            print(f"❌ 文本聊天测试失败: {response.status_code}")
            print(f"错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 文本聊天测试异常: {e}")
        return False

def test_image_upload(image_path: str, message: str = "请分析这张图片"):
    """测试图像上传和分析"""
    try:
        if not os.path.exists(image_path):
            print(f"❌ 图像文件不存在: {image_path}")
            return False
            
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
            data = {'message': message}
            
            response = requests.post(f"{BASE_URL}/upload-image", files=files, data=data)
            
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 图像分析测试成功")
            print(f"📸 文件: {os.path.basename(image_path)}")
            print(f"📝 分析结果: {result['analysis'][:200]}...")
            return True
        else:
            print(f"❌ 图像分析测试失败: {response.status_code}")
            print(f"错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 图像分析测试异常: {e}")
        return False

def test_model_info():
    """测试模型信息"""
    try:
        response = requests.get(f"{BASE_URL}/model-info")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 模型信息测试成功")
            print(f"🤖 模型端点: {result.get('model_endpoint', 'N/A')}")
            print(f"🔧 项目ID: {result.get('project_id', 'N/A')}")
            print(f"📍 位置: {result.get('location', 'N/A')}")
            return True
        else:
            print(f"❌ 模型信息测试失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 模型信息测试异常: {e}")
        return False

def run_comprehensive_test():
    """运行综合测试"""
    print("🚀 开始综合测试...")
    print("=" * 50)
    
    # 测试 API 健康状态
    print("\n1. 测试 API 健康状态")
    if not test_api_health():
        print("API 不可用，请检查服务器是否启动")
        return
    
    # 测试模型信息
    print("\n2. 测试模型信息")
    test_model_info()
    
    # 测试文本聊天
    print("\n3. 测试文本聊天")
    test_text_chat()
    
    # 测试图像分析
    print("\n4. 测试图像分析")
    
    # 查找测试图像
    test_images = []
    if os.path.exists(TEST_IMAGES_DIR):
        for filename in os.listdir(TEST_IMAGES_DIR):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                test_images.append(os.path.join(TEST_IMAGES_DIR, filename))
    
    if test_images:
        for image_path in test_images[:3]:  # 测试前3张图片
            print(f"\n📸 测试图像: {os.path.basename(image_path)}")
            test_image_upload(image_path, "请详细分析这张图片，并推荐相关的马来西亚旅游体验")
    else:
        print("❌ 没有找到测试图像")
        print(f"请在 {TEST_IMAGES_DIR} 目录下放置一些测试图片")
    
    print("\n" + "=" * 50)
    print("✅ 综合测试完成")

def create_test_request_examples():
    """创建测试请求示例"""
    examples = {
        "text_chat": {
            "url": f"{BASE_URL}/chat",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": {
                "message": "推荐一些马来西亚的特色美食",
                "temperature": 0.7,
                "max_tokens": 1000
            }
        },
        "image_upload": {
            "url": f"{BASE_URL}/upload-image",
            "method": "POST",
            "description": "使用 multipart/form-data 上传图片",
            "form_data": {
                "file": "图片文件",
                "message": "这是什么食物？推荐马来西亚的类似菜品"
            }
        }
    }
    
    print("\n📋 API 测试示例:")
    print(json.dumps(examples, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "health":
            test_api_health()
        elif command == "chat":
            test_text_chat()
        elif command == "model":
            test_model_info()
        elif command == "image" and len(sys.argv) > 2:
            test_image_upload(sys.argv[2])
        elif command == "examples":
            create_test_request_examples()
        else:
            print("使用方法:")
            print("  python test_image_analysis.py health    # 测试 API 健康")
            print("  python test_image_analysis.py chat      # 测试文本聊天")
            print("  python test_image_analysis.py model     # 测试模型信息")
            print("  python test_image_analysis.py image <path> # 测试图像分析")
            print("  python test_image_analysis.py examples  # 显示 API 示例")
            print("  python test_image_analysis.py          # 运行综合测试")
    else:
        run_comprehensive_test()