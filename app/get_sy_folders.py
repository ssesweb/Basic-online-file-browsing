import os
import ctypes
import ctypes.wintypes
import winreg
try:
    from win32com.shell import shell, shellcon
    HAS_WIN32COM = True
except ImportError:
    print('[初始化警告] 未找到win32com模块，部分功能将不可用')
    HAS_WIN32COM = False

def get_system_folder(folder_name):
    """
    获取系统文件夹路径（多方法组合）
    :param folder_name: 文件夹名称（中文）
    :return: 文件夹路径或None
    """
    # 方法1：Python标准库方法（优先尝试）
    folder_map = {
        '桌面': ['Desktop', '桌面', '我的桌面', '我的电脑桌面'],
        '文档': ['Documents', 'My Documents', '我的文档', '文档'],
        '下载': ['D:\\Download', 'Downloads', '下载', '我的下载'],
        '图片': ['Pictures', 'My Pictures', '我的图片', '图片'],
        '音乐': ['Music', 'My Music', '我的音乐', '音乐'],
        '视频': ['Videos', 'My Videos', '我的视频', '视频'],
        'OneDrive': ['OneDrive', '我的云盘', 'OneDrive商业版']
    }
    
    if folder_name in folder_map:
        print(f'[标准方法] 开始检测 {folder_name} 路径')
        for variant in folder_map[folder_name]:
            path = os.path.join(os.path.expanduser('~'), variant) if not variant.startswith('D:\\') else variant
            print(f'[标准方法] 尝试路径: {path}')
            if os.path.exists(path):
                print(f'[标准方法] 找到有效路径: {path}')
                return path
        print(f'[标准方法] 所有候选路径均无效')
    
    # 方法2：ctypes系统API方法
    csidl_map = {
        '桌面': 0,        # CSIDL_DESKTOP
        '文档': 5,        # CSIDL_PERSONAL
        '下载': 0x001c,   # CSIDL_DOWNLOADS
        '图片': 39,       # CSIDL_MYPICTURES
        '音乐': 13,       # CSIDL_MYMUSIC
        '视频': 14        # CSIDL_MYVIDEO
    }
    
    if folder_name in csidl_map:
        try:
            buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            if ctypes.windll.shell32.SHGetFolderPathW(None, 
                                                    csidl_map[folder_name],
                                                    None, 0, buf) == 0:
                if buf.value and os.path.exists(buf.value):
                    print(f'[系统API] 成功获取 {folder_name} 路径: {buf.value}')
                    return buf.value
                else:
                    d_path = os.path.join('D:\\', 'Download')
                    if os.path.exists(d_path):
                        print(f'[系统API] 使用备用路径: {d_path}')
                        return d_path
                print(f'[系统API] 无法获取 {folder_name} 路径')
        except Exception as e:
            print(f'[系统API] 调用异常: {str(e)}')
    
    # 方法3：win32com备用方法
    if HAS_WIN32COM:
        shell_csidl_map = {
            '桌面': shellcon.CSIDL_DESKTOP,
            '文档': shellcon.CSIDL_PERSONAL,
            '下载': shellcon.CSIDL_DOWNLOADS,
            '图片': shellcon.CSIDL_MYPICTURES,
            '音乐': shellcon.CSIDL_MYMUSIC,
            '视频': shellcon.CSIDL_MYVIDEO
        }
        
        if folder_name in shell_csidl_map:
            try:
                path = shell.SHGetFolderPath(0, shell_csidl_map[folder_name], None, 0)
                if path and os.path.exists(path):
                    print(f'[COM API] 成功获取 {folder_name} 路径: {path}')
                    return path
                else:
                    print(f'[COM API] 路径不存在: {path}')
            except Exception as e:
                print(f'[COM API] 调用异常: {str(e)}')
    
    # 方法4：注册表查询方法
    try:
        reg_path = r'Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
            downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
            path, _ = winreg.QueryValueEx(key, downloads_guid)
            expanded_path = os.path.expandvars(path)
            if os.path.exists(expanded_path):
                print(f'[注册表] 找到有效路径: {expanded_path}')
                return expanded_path
            else:
                print(f'[注册表] 路径不存在: {expanded_path}')
    except Exception as e:
        print(f'[注册表] 查询失败: {str(e)}')
    
    print(f'[最终结果] 未能找到 {folder_name} 的有效路径')
    return None
