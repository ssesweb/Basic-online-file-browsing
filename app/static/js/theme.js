// 主题初始化脚本，确保页面加载前应用正确主题
(function() {
    try {
        // 统一使用'theme'作为键名，兼容旧版'darkMode'键名
        var theme = localStorage.getItem('theme');
        var darkMode = localStorage.getItem('darkMode');
        
        // 兼容处理：如果有旧版存储但没有新版存储，则进行转换
        if (!theme && darkMode === 'true') {
            theme = 'dark';
            localStorage.setItem('theme', 'dark');
        }
        
        if (!theme) {
            // 如果没有设置，默认跟随系统
            theme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }
        
        if (theme === 'dark') {
            document.documentElement.classList.add('dark-mode');
            document.documentElement.style.setProperty('color-scheme', 'dark');
            if (document.body) {
                document.body.classList.add('dark-mode');
                document.body.classList.add('bg-dark');
                document.body.classList.remove('bg-light');
            }
        } else {
            document.documentElement.classList.remove('dark-mode');
            document.documentElement.style.setProperty('color-scheme', 'light');
            if (document.body) {
                document.body.classList.remove('dark-mode');
                document.body.classList.remove('bg-dark');
                document.body.classList.add('bg-light');
            }
        }
    } catch (e) {
        // 容错处理
        console.error('主题初始化出错:', e);
    }
})();