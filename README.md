# 局域网在线浏览器项目
## 项目简介
基于Python Flask和JavaScript开发的局域网文件浏览器，支持文件管理、多媒体预览和多设备访问。

## 核心功能

### 文件管理
- 多列/列表视图切换
- 智能文件排序（名称/大小/修改时间）
- 实时路径导航与快速跳转
- 系统特殊文件夹快捷访问（桌面/文档/下载等）

### 媒体处理
- 视频缩略图自动生成（支持MP4/AVI/MOV/MKV）
- 智能缓存清理机制（自动维护500MB缓存空间）
- 内嵌视频播放器（支持进度条/全屏控制）
- MIME类型自动识别（视频/图片/文档等）

### 系统特性
- 端口自动探测（5000-6000范围）
- 响应式布局（PC/平板/手机适配）
- 暗色/亮色主题切换
- 实时文件状态监控（大小/修改时间）

### 界面预览
![文件浏览视图](./docs/Preview/文件浏览视图.png)
![移动端界面](./docs/Preview/移动端.png)
![视频播放视图](./docs/Preview/视频视图.png)
![首页截图](./docs/Preview/首页截图.png)

## 快速开始

### 环境要求
- Python 3.8+
- FFmpeg（视频缩略图生成依赖）

1. 安装依赖：
```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装FFmpeg（Windows）
winget install -e --id Gyan.FFmpeg
```

2. 启动服务：

**最简单启动方式**
双击运行 `run_user.bat` 文件，按照提示选择模式即可启动服务。
启动完成后，脚本会显示访问地址 http://localhost:5000 方便用户直接访问服务。