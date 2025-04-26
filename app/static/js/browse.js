// 视图切换功能
document.addEventListener('DOMContentLoaded', function() {
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
    
    // 从本地存储中获取上次选择的列数模式
    const savedColsMode = localStorage.getItem('colsMode');
    if (savedColsMode && gridContainer) {
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
                
                // 保存列数模式到本地存储
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