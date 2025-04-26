import os
import ctypes
import ctypes.wintypes
try:
    from win32com.shell import shell, shellcon
    HAS_WIN32COM = True
except ImportError:
    HAS_WIN32COM = False

def get_system_folder(folder_name):
    """
    获取系统文件夹路径（多方法组合）
    :param folder_name: 文件夹名称（中文）
    :return: 文件夹路径或None
    """
    # 方法1：Python标准库方法（优先尝试）
    folder_map = {
        '桌面': ['Desktop', '桌面', '我的桌面'],
        '文档': ['Documents', '我的文档', '文档'],
        '下载': ['Downloads', '下载', '我的下载'],
        '图片': ['Pictures', '我的图片', '图片'],
        '音乐': ['Music', '我的音乐', '音乐'],
        '视频': ['Videos', '我的视频', '视频'],
        'OneDrive': ['OneDrive', '我的云盘']
    }
    
    if folder_name in folder_map:
        for variant in folder_map[folder_name]:
            path = os.path.join(os.path.expanduser('~'), variant)
            if os.path.exists(path):
                return path
    
    # 方法2：ctypes方法（如果标准方法失败）
    if folder_name == '图片':
        try:
            buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            # 用CSIDL_MYPICTURES代替数字39
            if ctypes.windll.shell32.SHGetFolderPathW(None, 
                                                        39, #ctypes.windll.shell32.CSIDL_MYPICTURES,  # 这行代码会报错，因为ctypes里没有CSIDL_MYPICTURES
                                                        None, 0, buf) == 0:
                return buf.value
        except Exception:
            pass
    
    # 方法3：win32com方法（如果前两种方法都失败）
    if HAS_WIN32COM and folder_name == '图片':
        try:
            # 用shellcon.CSIDL_MYPICTURES代替数字39
            path = shell.SHGetFolderPath(0, shellcon.CSIDL_MYPICTURES, None, 0)
            if path and os.path.exists(path):
                return path
        except Exception:
            pass
    
    return None
