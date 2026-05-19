// 本地圖片管理器
class LocalImageManager {
    // 獲取圖片路徑
    getImagePath(text) {
        return `images/${text}.jpg`;
    }
}

// 創建全域本地圖片管理器
window.localImageManager = new LocalImageManager();
