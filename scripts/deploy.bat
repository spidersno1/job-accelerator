@echo off
setlocal enabledelayedexpansion

echo 🚀 开始部署程序员求职加速器Agent...

:: 检查参数
if "%1"=="" (
    echo 用法: %0 {install^|build^|dev^|all}
    echo   install - 安装所有依赖
    echo   build   - 构建前端应用
    echo   dev     - 启动开发服务器
    echo   all     - 完整部署流程
    exit /b 1
)

:: 检查必要的工具
echo 📋 检查部署要求...

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js 未安装
    exit /b 1
)

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 未安装
    exit /b 1
)

where git >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git 未安装
    exit /b 1
)

echo ✅ 所有要求已满足

if "%1"=="install" goto install
if "%1"=="build" goto build
if "%1"=="dev" goto dev
if "%1"=="all" goto all

:install
echo 🔧 安装后端依赖...
cd backend
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
cd ..
echo ✅ 后端依赖安装完成

echo 🔧 安装前端依赖...
cd frontend
npm install
cd ..
echo ✅ 前端依赖安装完成
goto end

:build
echo 🏗️ 构建前端应用...
cd frontend
call npm run build
if errorlevel 1 (
    echo 前端构建失败
    exit /b 1
)
cd ..
echo ✅ 前端构建完成
goto end

:dev
echo 🚀 启动开发服务器...
start "Backend" cmd /k "cd backend && venv\Scripts\activate.bat && python main.py"
timeout /t 3 /nobreak >nul
start "Frontend" cmd /k "cd frontend && npm run dev"
echo ✅ 开发服务器已启动
echo 📱 前端: http://localhost:3000
echo 🔧 后端: http://localhost:8000
echo 📚 API文档: http://localhost:8000/docs
goto end

:all
echo 🔧 安装后端依赖...
cd backend
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
cd ..

echo 🔧 安装前端依赖...
cd frontend
npm install
cd ..

echo 🏗️ 构建前端应用...
cd frontend
call npm run build
if errorlevel 1 (
    echo 前端构建失败
    exit /b 1
)
cd ..

echo 🚀 启动开发服务器...
start "Backend" cmd /k "cd backend && venv\Scripts\activate.bat && python main.py"
timeout /t 3 /nobreak >nul
start "Frontend" cmd /k "cd frontend && npm run dev"
echo ✅ 开发服务器已启动
echo 📱 前端: http://localhost:3000
echo 🔧 后端: http://localhost:8000
echo 📚 API文档: http://localhost:8000/docs

:end
echo 🎉 部署完成！
pause