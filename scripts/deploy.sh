#!/bin/bash

# 程序员求职加速器Agent 部署脚本

echo "🚀 开始部署程序员求职加速器Agent..."

# 检查必要的工具
check_requirements() {
    echo "📋 检查部署要求..."
    
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js 未安装"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python3 未安装"
        exit 1
    fi
    
    if ! command -v git &> /dev/null; then
        echo "❌ Git 未安装"
        exit 1
    fi
    
    echo "✅ 所有要求已满足"
}

# 安装后端依赖
install_backend() {
    echo "🔧 安装后端依赖..."
    cd backend
    
    # 创建虚拟环境
    python3 -m venv venv
    source venv/bin/activate
    
    # 安装依赖
    pip install -r requirements.txt
    
    echo "✅ 后端依赖安装完成"
    cd ..
}

# 安装前端依赖
install_frontend() {
    echo "🔧 安装前端依赖..."
    cd frontend
    
    # 安装依赖
    npm install
    
    echo "✅ 前端依赖安装完成"
    cd ..
}

# 构建前端
build_frontend() {
    echo "🏗️ 构建前端应用..."
    cd frontend
    
    # 构建生产版本
    npm run build
    
    echo "✅ 前端构建完成"
    cd ..
}

# 启动开发服务器
start_dev() {
    echo "🚀 启动开发服务器..."
    
    # 启动后端
    cd backend
    source venv/bin/activate
    python main.py &
    BACKEND_PID=$!
    cd ..
    
    # 启动前端
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo "✅ 开发服务器已启动"
    echo "📱 前端: http://localhost:3000"
    echo "🔧 后端: http://localhost:8000"
    echo "📚 API文档: http://localhost:8000/docs"
    
    # 等待用户中断
    echo "按 Ctrl+C 停止服务器"
    wait
}

# 清理进程
cleanup() {
    echo "🧹 清理进程..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 主函数
main() {
    case "$1" in
        "install")
            check_requirements
            install_backend
            install_frontend
            ;;
        "build")
            build_frontend
            ;;
        "dev")
            start_dev
            ;;
        "all")
            check_requirements
            install_backend
            install_frontend
            build_frontend
            start_dev
            ;;
        *)
            echo "用法: $0 {install|build|dev|all}"
            echo "  install - 安装所有依赖"
            echo "  build   - 构建前端应用"
            echo "  dev     - 启动开发服务器"
            echo "  all     - 完整部署流程"
            exit 1
            ;;
    esac
}

main "$@" 
 