@echo off

REM 检查Python依赖
pip show flask >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 缺失Python依赖，请执行以下命令安装：
    echo pip install -r requirements.txt
    pause
    exit /b 1
)

REM 检查FFmpeg
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] FFmpeg未安装，请执行以下命令安装：
    echo winget install -e --id Gyan.FFmpeg
    pause
    exit /b 1
)

REM 检查node_modules
if not exist "node_modules" (
    echo [提示] 前端依赖未安装，请执行：
    echo npm install
)

echo 环境检查通过！