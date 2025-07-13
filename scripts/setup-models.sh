#!/bin/bash

# Ollama模型自动安装脚本
# 安装免费AI模型用于零成本运行

echo "🚀 开始安装免费AI模型..."

# 等待Ollama服务启动
echo "⏳ 等待Ollama服务启动..."
while ! curl -f http://localhost:11434/api/tags >/dev/null 2>&1; do
    echo "等待Ollama服务..."
    sleep 5
done

echo "✅ Ollama服务已启动"

# 安装中文优化模型 - Qwen2.5:7B
echo "📥 安装中文优化模型: qwen2.5:7b"
if ollama pull qwen2.5:7b; then
    echo "✅ qwen2.5:7b 安装成功"
else
    echo "❌ qwen2.5:7b 安装失败，尝试备用模型"
fi

# 安装通用模型 - Llama3.1:8B
echo "📥 安装通用模型: llama3.1:8b"
if ollama pull llama3.1:8b; then
    echo "✅ llama3.1:8b 安装成功"
else
    echo "❌ llama3.1:8b 安装失败"
fi

# 安装代码专用模型 - CodeLlama:7B
echo "📥 安装代码专用模型: codellama:7b"
if ollama pull codellama:7b; then
    echo "✅ codellama:7b 安装成功"
else
    echo "❌ codellama:7b 安装失败"
fi

# 检查安装的模型
echo "📋 检查已安装的模型:"
ollama list

# 测试模型是否工作正常
echo "🧪 测试模型功能..."

# 测试中文模型
echo "测试中文模型..."
if echo '{"model":"qwen2.5:7b","prompt":"你好，请简单介绍一下自己。","stream":false}' | curl -s -X POST http://localhost:11434/api/generate -d @- | grep -q "response"; then
    echo "✅ 中文模型测试成功"
else
    echo "⚠️ 中文模型测试失败"
fi

# 测试通用模型
echo "测试通用模型..."
if echo '{"model":"llama3.1:8b","prompt":"Hello, please introduce yourself briefly.","stream":false}' | curl -s -X POST http://localhost:11434/api/generate -d @- | grep -q "response"; then
    echo "✅ 通用模型测试成功"
else
    echo "⚠️ 通用模型测试失败"
fi

echo "🎉 模型安装和测试完成！"

# 显示系统信息
echo "💾 系统信息:"
echo "可用内存: $(free -h | awk '/^Mem:/ {print $7}')"
echo "磁盘空间: $(df -h /root/.ollama | awk 'NR==2 {print $4}')"

echo "🔗 Ollama服务地址: http://localhost:11434"
echo "📊 查看模型列表: http://localhost:11434/api/tags"

# 保持服务运行
echo "🎯 模型安装完成，Ollama服务继续运行..." 