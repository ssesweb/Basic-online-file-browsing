// 视图切换功能
document.addEventListener('DOMContentLoaded', function() {
    // 实现视频缩略图懒加载功能
    const lazyLoadThumbnails = function() {
        // 使用Intersection Observer API监测元素是否进入视口
        const observer = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                // 当元素进入视口时
                if (entry.isIntersecting) {
                    const img = entry.target;
                    // 将data-src的值赋给src属性，触发图片加载
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        // 加载后不再需要观察此元素
                        observer.unobserve(img);
                    }
                }
            });
        }, {
            // 设置根元素为null表示视口
            root: null,
            // 元素进入视口20%时触发加载
            threshold: 0.2,
            // 视口外100px处开始预加载
            rootMargin: '100px'
        });

        // 获取所有带有lazy-thumbnail类的图片元素
        const lazyImages = document.querySelectorAll('.lazy-thumbnail');
        lazyImages.forEach(img => {
            observer.observe(img);
        });
    };

    // 初始化懒加载
    lazyLoadThumbnails();
    
    // 视图切换按钮
    const viewButtons = document.querySelectorAll('.view-btn');
    const viewList = document.querySelector('.view-list');
    const viewGrid = document.querySelector('.view-grid');
    
    // 从本地存储中获取上次选择的视图模式
    const savedView = localStorage.getItem('viewMode');
    if (savedView) {
        if (savedView === 'grid' && viewGrid) {
            viewList.classList.add('d-none');
            viewGrid.classList.remove('d-none');
            viewButtons.forEach(btn => {
                btn.classList.remove('active');
                if (btn.dataset.view === 'grid') {
                    btn.classList.add('active');
                }
            });
        }
    }
    
    // 视图切换事件监听
    viewButtons.forEach(button => {
        button.addEventListener('click', function() {
            const viewMode = this.dataset.view;
            
            // 移除所有按钮的active类
            viewButtons.forEach(btn => btn.classList.remove('active'));
            
            // 添加当前按钮的active类
            this.classList.add('active');
            
            // 切换视图
            if (viewMode === 'list') {
                viewList.classList.remove('d-none');
                viewGrid.classList.add('d-none');
            } else if (viewMode === 'grid') {
                viewList.classList.add('d-none');
                viewGrid.classList.remove('d-none');
            }
            
            // 保存视图模式到本地存储
            localStorage.setItem('viewMode', viewMode);
        });
    });
    
    // 列数选择功能
    const colsModeLinks = document.querySelectorAll('.cols-mode');
    const gridContainer = document.querySelector('.view-grid');
    
    // 设置cookie函数
    function setCookie(name, value, days) {
        let expires = "";
        if (days) {
            const date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = "; expires=" + date.toUTCString();
        }
        document.cookie = name + "=" + (value || "") + expires + "; path=/";
    }
    
    // 获取cookie函数
    function getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for(let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    }
    
    // 从cookie中获取上次选择的列数模式，如果没有则默认为"auto"
    const savedColsMode = getCookie('colsMode') || localStorage.getItem('colsMode') || "auto";
    if (gridContainer) {
        applyColsMode(savedColsMode, gridContainer);
        
        // 更新下拉菜单中的选中状态
        colsModeLinks.forEach(link => {
            if (link.dataset.cols === savedColsMode) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }
    
    // 列数选择事件监听
    colsModeLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const colsMode = this.dataset.cols;
            
            // 移除所有链接的active类
            colsModeLinks.forEach(l => l.classList.remove('active'));
            
            // 添加当前链接的active类
            this.classList.add('active');
            
            // 应用列数模式
            if (gridContainer) {
                applyColsMode(colsMode, gridContainer);
                
                // 保存列数模式到cookie和本地存储（保留30天）
                setCookie('colsMode', colsMode, 30);
                localStorage.setItem('colsMode', colsMode);
            }
        });
    });
    
    // 应用列数模式的函数
    function applyColsMode(mode, container) {
        // 移除所有可能的列数类
        container.classList.remove('row-cols-1', 'row-cols-2', 'row-cols-md-3', 'row-cols-md-4', 'row-cols-md-5', 'row-cols-lg-6', 'row-cols-lg-8', 'compact-mode');
        
        // 根据模式应用相应的类
        if (mode === '1') {
            container.classList.add('row-cols-1');
        } else if (mode === '2') {
            container.classList.add('row-cols-2');
        } else if (mode === 'auto') {
            container.classList.add('row-cols-md-4', 'row-cols-lg-6');
        } else if (mode === 'compact') {
            container.classList.add('row-cols-md-5', 'row-cols-lg-8', 'compact-mode');
        }
    }
});