# 微调模型配置说明

## 概述
你的系统已经配置为使用 Gemini 2.5 Flash 微调模型进行图像分析。该配置支持计算机视觉功能，可以分析用户上传的图片并提供相关的马来西亚旅游建议。

## 环境变量配置

### 1. 基本配置
在你的 `.env` 文件中设置以下环境变量：

```env
# 你的 Google Cloud 项目信息
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=us-west1

# 你的微调模型端点
VERTEX_AI_ENDPOINT=projects/your_project_id/locations/us-west1/endpoints/your_endpoint_id

# Google Cloud 服务账号 JSON（用于认证）
GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON=your_service_account_json_string

# Gemini API Key（备用）
GEMINI_API_KEY=your_gemini_api_key
```

### 2. 微调模型特定配置
- **模型类型**: Gemini 2.5 Flash 微调模型
- **支持功能**: 文本生成 + 计算机视觉
- **优化配置**:
  - Temperature: 0.4 (平衡创造性和准确性)
  - Max Output Tokens: 1500 (支持详细分析)
  - Top P: 0.9
  - Top K: 40

## 图像分析功能

### 支持的图像格式
- JPEG
- PNG
- WebP
- 最大文件大小: 10MB

### 分析能力
你的微调模型将能够：

1. **食物识别**: 识别菜品并推荐马来西亚类似美食
2. **地标识别**: 分析建筑和景点，推荐马来西亚相似地点
3. **文化元素**: 识别文化特色并关联到马来西亚体验
4. **自然景观**: 分析风景并推荐马来西亚相似的自然景点

### 工作流程
1. 用户上传图像
2. 系统使用你的微调模型进行分析
3. 模型以 Aiman 角色提供个性化的马来西亚旅游建议
4. 如果主模型失败，会自动降级到标准 Gemini 2.0 Flash

## 代码更新

### 主要修改
1. **`analyze_image_with_gemini` 函数**: 
   - 优先使用你的微调模型
   - 专门的提示词设计
   - 多层次错误处理

2. **模型配置**:
   - 针对图像分析优化的参数
   - 流式和非流式生成的备用方案

3. **错误处理**:
   - 自动降级到备用模型
   - 友好的错误提示

## 测试建议

### 测试用例
1. **食物图片**: 上传不同类型的食物图片
2. **建筑图片**: 测试地标和建筑识别
3. **风景图片**: 测试自然景观分析
4. **文化图片**: 测试文化元素识别

### 期望结果
- 准确的图像描述
- 相关的马来西亚旅游建议
- 保持 Aiman 角色的一致性
- 友好和有帮助的回复风格

## 部署注意事项

1. 确保所有环境变量正确设置
2. 验证 Google Cloud 认证配置
3. 测试微调模型的访问权限
4. 监控模型性能和响应时间

## 故障排除

### 常见问题
1. **模型访问失败**: 检查端点配置和认证
2. **图像处理失败**: 验证图像格式和大小
3. **响应质量**: 调整温度和其他参数

### 日志监控
查看这些日志关键字：
- `🎯 Using fine-tuned Gemini 2.5 Flash model`
- `📸 Created image content for fine-tuned model`
- `🤖 Generated image analysis with fine-tuned model`