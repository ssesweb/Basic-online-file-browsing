// 视频缩略图懒加载增强脚本
document.addEventListener('DOMContentLoaded', function() {
    // 实现视频缩略图懒加载功能
    const lazyLoadThumbnails = function() {
        // 使用Intersection Observer API监测元素是否进入视口
        const observer = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                // 当元素进入视口时
                if (entry.isIntersecting) {
                    const img = entry.target;
                    // 获取缩略图路径
                    const thumbnailPath = img.dataset.src;
                    if (thumbnailPath) {
                        // 检查是否需要生成缩略图
                        fetch(thumbnailPath)
                            .then(response => {
                                if (response.ok) {
                                    // 缩略图已存在，直接加载
                                    img.src = thumbnailPath;
                                } else {
                                    // 缩略图不存在，显示占位图
                                    img.src = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PGNpcmNsZSBjeD0iNTAiIGN5PSI1MCIgcj0iNDAiIGZpbGw9IiM2YzZjNmMiLz48cGF0aCBkPSJNNDAgMzBMNzAgNTAgNDAgNzB6IiBmaWxsPSIjZmZmIi8+PC9zdmc+';
                                }
                            })
                            .catch(error => {
                                console.error('加载缩略图失败:', error);
                                // 加载失败时显示占位图
                                img.src = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PGNpcmNsZSBjeD0iNTAiIGN5PSI1MCIgcj0iNDAiIGZpbGw9IiM2YzZjNmMiLz48cGF0aCBkPSJNNDAgMzBMNzAgNTAgNDAgNzB6IiBmaWxsPSIjZmZmIi8+PC9zdmc+';
                            });
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

    // 视图切换时重新初始化懒加载
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            // 延迟执行，确保DOM已更新
            setTimeout(lazyLoadThumbnails, 100);
        });
    });
});