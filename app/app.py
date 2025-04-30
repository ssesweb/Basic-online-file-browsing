from flask import Flask, render_template, send_from_directory, request
import os
import subprocess
import tempfile
import socket
from datetime import datetime

app = Flask(__name__)

# 添加自定义过滤器
@app.template_filter('datetime')
def format_datetime(timestamp, format="%Y-%m-%d %H:%M:%S"):
    return datetime.fromtimestamp(timestamp).strftime(format)

@app.template_filter('filesizeformat')
def format_filesize(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

# 注册过滤器
app.jinja_env.filters['filesizeformat'] = format_filesize

@app.route('/')
def index():
    # 获取系统盘符
    drives = [f"{d}:\\" for d in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if os.path.exists(f"{d}:\\")]
    
    # 获取系统文件夹路径 - 使用多方法组合
    from get_sy_folders import get_system_folder
    
    system_folders = [
        '桌面', '文档', '下载', '图片', '音乐', '视频', 'OneDrive'
    ]
    
    valid_folders = {}
    try:
        for name in system_folders:
            path = get_system_folder(name)
            if path:
                valid_folders[name] = path
    except Exception as e:
        print(f"路径获取失败: {e}")
    
    return render_template('index.html', drives=drives, system_folders=valid_folders)

@app.route('/browse/<path:dirpath>')
def browse(dirpath):
    # 获取目录内容
    try:
        items = os.listdir(dirpath)
        files = []
        dirs = []
        for item in items:
            full_path = os.path.join(dirpath, item)
            if os.path.isdir(full_path):
                dirs.append({
                    'name': item,
                    'path': full_path
                })
            else:
                # 检查是否为视频文件，如果是则准备缩略图路径（但不立即生成）
                thumbnail_path = None
                ext = os.path.splitext(item)[1].lower()
                if ext in ['.mp4', '.avi', '.mov', '.mkv']:
                    # 只计算缩略图文件名，不立即生成缩略图
                    import hashlib
                    video_hash = hashlib.md5(full_path.encode()).hexdigest()
                    thumbnail_path = f"{video_hash}.jpg"
                
                files.append({
                    'name': item,
                    'size': os.path.getsize(full_path),
                    'modified': os.path.getmtime(full_path),
                    'thumbnail': thumbnail_path
                })
        
        # 根据用户选择的排序方式对文件列表进行排序
        sort_by = request.args.get('sort', 'name')  # 默认按名称排序
        sort_dir = request.args.get('dir', 'asc')  # 默认升序
        reverse_sort = sort_dir == 'desc'
        
        if sort_by == 'name':
            files.sort(key=lambda x: x['name'].lower(), reverse=reverse_sort)
        elif sort_by == 'size':
            files.sort(key=lambda x: x['size'], reverse=reverse_sort)
        elif sort_by == 'modified':
            files.sort(key=lambda x: x['modified'], reverse=not reverse_sort if sort_dir == 'asc' else reverse_sort)
            
        # 按名称排序目录
        dirs.sort(key=lambda x: x['name'].lower())
            
        return render_template('browse.html', dirs=dirs, files=files, current_path=dirpath)
    except Exception as e:
        return str(e), 404

# 视频缩略图生成函数
def generate_video_thumbnail(video_path):
    import os
    try:
        # 创建缩略图目录
        thumbnails_dir = os.path.join(app.root_path, 'static', 'thumbnails')
        os.makedirs(thumbnails_dir, exist_ok=True)
        
        # 添加自动清理机制
        clean_thumbnail_cache(thumbnails_dir)
        
        # 使用视频文件的哈希值作为缩略图文件名，确保唯一性
        import hashlib
        video_hash = hashlib.md5(video_path.encode()).hexdigest()
        thumbnail_filename = f"{video_hash}.jpg"
        thumbnail_path = os.path.join(thumbnails_dir, thumbnail_filename)
        
        # 如果缩略图已存在，直接返回
        if os.path.exists(thumbnail_path) and os.path.getsize(thumbnail_path) > 0:
            return thumbnail_filename
        
        # 尝试提取第5秒的帧
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-ss', '00:00:05',  # 第5秒
            '-frames:v', '1',
            '-q:v', '2',
            thumbnail_path
        ]
        
        # 修改这里：添加encoding参数解决编码问题
        result = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='ignore', timeout=10)
        
        # 如果提取第5秒失败，则尝试提取首帧
        if result.returncode != 0:
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-frames:v', '1',
                '-q:v', '2',
                thumbnail_path
            ]
            subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='ignore', timeout=10)
        
        # 检查缩略图是否成功生成
        if os.path.exists(thumbnail_path) and os.path.getsize(thumbnail_path) > 0:
            return thumbnail_filename
        else:
            return None
    except Exception as e:
        print(f"生成视频缩略图失败: {e}")
        return None

# 在download路由前添加MIME类型映射
MIME_MAP = {
    'mp4': 'video/mp4',
    'avi': 'video/x-msvideo',
    'mov': 'video/quicktime',
    'mkv': 'video/x-matroska'
}

@app.route('/download/<path:filepath>')
def download(filepath):
    directory, filename = os.path.split(filepath)
    # 设置as_attachment=False以允许浏览器直接显示内容
    response = send_from_directory(directory, filename, as_attachment=False)
    # 添加MIME类型
    ext = filename.split('.')[-1].lower()
    if ext in MIME_MAP:
        response.headers['Content-Type'] = MIME_MAP[ext]
    return response

@app.route('/play_video/<path:filepath>')
def play_video(filepath):
    """视频播放页面"""
    try:
        directory, filename = os.path.split(filepath)
        # 自动获取当前路径
        current_path = os.path.dirname(filepath)
        
        # 获取文件信息
        file_stats = os.stat(filepath)
        filesize = file_stats.st_size
        modified = file_stats.st_mtime
        
        # 获取MIME类型
        ext = filename.split('.')[-1].lower()
        mime_type = MIME_MAP.get(ext, 'video/mp4')
        
        return render_template('video_player.html', 
                              filepath=filepath,
                              filename=filename,
                              directory=directory,
                              filesize=filesize,
                              modified=modified,
                              mime_type=mime_type,
                              current_path=current_path)                              
    except Exception as e:
        return str(e), 404

@app.route('/thumbnail/<path:filepath>')
def thumbnail(filepath):
    """提供视频缩略图，如果不存在则按需生成"""
    # 从static/thumbnails目录提供缩略图
    thumbnails_dir = os.path.join(app.root_path, 'static', 'thumbnails')
    thumbnail_path = os.path.join(thumbnails_dir, filepath)
    
    # 检查缩略图是否存在，如果不存在则返回占位图
    if not os.path.exists(thumbnail_path) or os.path.getsize(thumbnail_path) == 0:
        # 这里不再尝试查找视频文件，而是在前端请求时通过路径参数生成
        pass
    
    # 如果缩略图存在则返回，否则返回404
    if os.path.exists(thumbnail_path) and os.path.getsize(thumbnail_path) > 0:
        return send_from_directory(thumbnails_dir, filepath, mimetype='image/jpeg')
    else:
        return '', 404

@app.route('/generate_thumbnail')
def generate_thumbnail():
    """按需生成视频缩略图"""
    video_path = request.args.get('video_path')
    if not video_path or not os.path.exists(video_path):
        return {'success': False, 'error': '视频文件不存在'}, 404
        
    # 生成缩略图
    thumbnail_filename = generate_video_thumbnail(video_path)
    if thumbnail_filename:
        return {'success': True, 'thumbnail': thumbnail_filename}
    else:
        return {'success': False, 'error': '生成缩略图失败'}, 500

# 在模板中注册文件类型检测函数
@app.context_processor
def utility_processor():
    return dict(
        get_file_icon=get_file_icon,
        os=os,
        get_file_color=get_file_color,
        now=datetime.now()  # 添加当前时间
    )

# 新增文件类型颜色映射函数
def get_file_color(filename):
    ext = os.path.splitext(filename)[1].lower()
    # 根据文件类型分组
    if ext in ['.pdf']:
        return 'pdf'
    elif ext in ['.doc', '.docx', '.txt', '.rtf', '.odt']:
        return 'document'
    elif ext in ['.xls', '.xlsx', '.csv', '.ods']:
        return 'spreadsheet'
    elif ext in ['.ppt', '.pptx', '.odp']:
        return 'presentation'
    elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']:
        return 'image'
    elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.webm']:
        return 'video'
    elif ext in ['.mp3', '.wav', '.ogg', '.flac', '.aac']:
        return 'audio'
    elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']:
        return 'archive'
    else:
        return 'default'

# 文件类型检测函数（增强版）
def get_file_icon(filename):
    ext = os.path.splitext(filename)[1].lower()
    # 扩展图标映射
    icon_map = {
        # 文档类
        '.pdf': 'fa-file-pdf',
        '.doc': 'fa-file-word',
        '.docx': 'fa-file-word',
        '.txt': 'fa-file-alt',
        '.rtf': 'fa-file-alt',
        '.odt': 'fa-file-word',
        
        # 表格类
        '.xls': 'fa-file-excel',
        '.xlsx': 'fa-file-excel',
        '.csv': 'fa-file-csv',
        '.ods': 'fa-file-excel',
        
        # 演示文稿
        '.ppt': 'fa-file-powerpoint',
        '.pptx': 'fa-file-powerpoint',
        '.odp': 'fa-file-powerpoint',
        
        # 图像类
        '.jpg': 'fa-file-image',
        '.jpeg': 'fa-file-image',
        '.png': 'fa-file-image',
        '.gif': 'fa-file-image',
        '.bmp': 'fa-file-image',
        '.svg': 'fa-file-image',
        '.webp': 'fa-file-image',
        
        # 视频类
        '.mp4': 'fa-file-video',
        '.avi': 'fa-file-video',
        '.mov': 'fa-file-video',
        '.mkv': 'fa-file-video',
        '.flv': 'fa-file-video',
        '.webm': 'fa-file-video',
        
        # 音频类
        '.mp3': 'fa-file-audio',
        '.wav': 'fa-file-audio',
        '.ogg': 'fa-file-audio',
        '.flac': 'fa-file-audio',
        '.aac': 'fa-file-audio',
        
        # 压缩文件
        '.zip': 'fa-file-archive',
        '.rar': 'fa-file-archive',
        '.7z': 'fa-file-archive',
        '.tar': 'fa-file-archive',
        '.gz': 'fa-file-archive',
        '.bz2': 'fa-file-archive',
        
        # 代码类
        '.html': 'fa-file-code',
        '.css': 'fa-file-code',
        '.js': 'fa-file-code',
        '.py': 'fa-file-code',
        '.java': 'fa-file-code',
        '.php': 'fa-file-code',
        '.c': 'fa-file-code',
        '.cpp': 'fa-file-code',
        '.json': 'fa-file-code',
        '.xml': 'fa-file-code',
    }
    return icon_map.get(ext, 'fa-file')

def clean_thumbnail_cache(cache_dir, max_size_mb=500, min_size_mb=10):
    """清理缓存文件夹，保持大小在合理范围内"""
    try:
        # 计算当前缓存大小(MB)
        total_size = sum(os.path.getsize(f) for f in os.scandir(cache_dir) if f.is_file()) / (1024*1024)
        
        if total_size > max_size_mb:
            print(f"缓存大小 {total_size:.2f}MB 超过限制 {max_size_mb}MB，开始清理...")
            
            # 获取所有文件并按修改时间排序(旧文件在前)
            files = sorted([f for f in os.scandir(cache_dir) if f.is_file()], 
                         key=lambda x: x.stat().st_mtime)
            
            # 逐个删除最旧的文件直到小于min_size_mb
            deleted_size = 0
            for file in files:
                if total_size - deleted_size <= min_size_mb:
                    break
                    
                file_size = os.path.getsize(file) / (1024*1024)
                try:
                    os.remove(file.path)
                    deleted_size += file_size
                    print(f"已删除旧缓存文件: {file.name} (大小: {file_size:.2f}MB)")
                except Exception as e:
                    print(f"删除文件 {file.name} 失败: {e}")
            
            print(f"清理完成，当前缓存大小: {total_size - deleted_size:.2f}MB")
    except Exception as e:
        print(f"清理缓存时出错: {e}")

def find_available_port(start=5000, end=6000):
    for port in range(start, end+1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(('0.0.0.0', port))
                return port
            except OSError:
                continue
    raise OSError("5000-6000所有端口都被占用了！")

if __name__ == '__main__':
    import webbrowser
    import threading
    import time
    
    port = find_available_port()
    print(f"终于找到能用的端口：{port} ,不要关闭这个窗口！")
    
    # 创建一个函数，延迟1秒后自动打开浏览器
    def open_browser():
        time.sleep(1)
        url = f"http://localhost:{port}"
        print(f"正在为您自动打开浏览器，访问地址: {url}")
        webbrowser.open(url)
    
    # 创建线程运行浏览器打开函数
    threading.Thread(target=open_browser).start()
    
    # 必须关掉debug模式的重载器，不然又他妈会检测两次
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=True)
