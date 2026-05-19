// --- 資料庫區 ---
// 結構說明： 
// text: 顯示文字
// initial: 目標聲母 (ㄅ, ㄆ, ㄇ...)
// syllables: 音節數 (2 或 3)
// targetIndex: 目標聲母在第幾個字 (0=首字, 1=第二字, 2=第三字)

let vocabularyDB = [];

let isVocabularyLoaded = false;
let vocabularyLoadError = null;

function flattenVocabularyList(list) {
    const out = [];
    for (const item of list) {
        if (Array.isArray(item)) {
            out.push(...flattenVocabularyList(item));
        } else {
            out.push(item);
        }
    }
    return out;
}

function isValidVocabularyItem(item) {
    return item &&
        typeof item === 'object' &&
        typeof item.text === 'string' &&
        typeof item.initial === 'string' &&
        (typeof item.syllables === 'number' || typeof item.syllables === 'string') &&
        (typeof item.targetIndex === 'number' || typeof item.targetIndex === 'string') &&
        item.text.trim().length > 0 &&
        item.initial.trim().length > 0;
}

// 從 vocabulary.json 載入詞彙資料
async function loadVocabulary() {
    try {
        isVocabularyLoaded = false;
        vocabularyLoadError = null;

        const response = await fetch('vocabulary.json', { cache: 'no-store' });
        if (!response.ok) {
            throw new Error(`HTTP ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        if (!data || !Array.isArray(data.vocabulary)) {
            throw new Error('vocabulary.json 格式錯誤：找不到 vocabulary 陣列');
        }

        const flattened = flattenVocabularyList(data.vocabulary);
        const validItems = flattened.filter(isValidVocabularyItem);
        vocabularyDB = validItems;
        isVocabularyLoaded = true;

        console.log(`已載入 ${vocabularyDB.length} 筆詞彙`);
        if (validItems.length !== flattened.length) {
            console.warn(`有 ${flattened.length - validItems.length} 筆資料格式不符合預期，已略過`);
        }
        
        // 顯示載入成功的訊息
        const loadStatus = document.createElement('div');
        loadStatus.id = 'loadStatus';
        loadStatus.style.color = 'green';
        loadStatus.style.fontSize = '14px';
        loadStatus.style.marginTop = '10px';
        loadStatus.textContent = `✓ 詞彙資料載入成功 (${vocabularyDB.length} 筆)`;
        
        // 移除舊的狀態訊息
        const oldStatus = document.getElementById('loadStatus');
        if (oldStatus) oldStatus.remove();
        
        // 插入新狀態訊息
        const searchSection = document.querySelector('.search-section');
        if (searchSection) {
            searchSection.appendChild(loadStatus);
        }
        
    } catch (error) {
        vocabularyLoadError = error;
        console.error('無法載入詞彙資料:', error);
        
        // 顯示載入失敗的訊息
        const loadStatus = document.createElement('div');
        loadStatus.id = 'loadStatus';
        loadStatus.style.color = 'red';
        loadStatus.style.fontSize = '14px';
        loadStatus.style.marginTop = '10px';
        loadStatus.textContent = `✗ 詞彙資料載入失敗: ${error.message}`;
        
        // 移除舊的狀態訊息
        const oldStatus = document.getElementById('loadStatus');
        if (oldStatus) oldStatus.remove();
        
        // 插入新狀態訊息
        const searchSection = document.querySelector('.search-section');
        if (searchSection) {
            searchSection.appendChild(loadStatus);
        }
    }
}

// 頁面載入時執行
document.addEventListener('DOMContentLoaded', () => {
    loadVocabulary();
    
    // 添加鍵盤支援
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            const targetInitial = document.getElementById('targetInitial');
            const positionType = document.getElementById('positionType');
            
            // 如果焦點在選擇器上，按 Enter 可以執行搜尋
            if (document.activeElement === targetInitial || document.activeElement === positionType) {
                searchWords();
            }
        }
    });
    
    // 為選擇器添加變更事件監聽器，提供即時反饋
    const targetInitial = document.getElementById('targetInitial');
    const positionType = document.getElementById('positionType');
    
    [targetInitial, positionType].forEach(element => {
        element.addEventListener('change', () => {
            // 如果兩個選擇器都有值，可以顯示提示
            if (targetInitial.value && positionType.value && isVocabularyLoaded) {
                console.log('可以開始搜尋了！');
            }
        });
    });
});



// --- 搜尋功能邏輯 ---
function searchWords() {
    // 1. 取得使用者輸入
    const targetInitial = document.getElementById('targetInitial').value;
    const positionType = document.getElementById('positionType').value;

    if (!isVocabularyLoaded) {
        const baseMsg = '詞彙資料尚未載入完成，請稍後再試。';
        const hint = window.location && window.location.protocol === 'file:'
            ? '\n\n提示：你目前可能是用 file:// 方式開啟頁面，瀏覽器會擋住 fetch。請改用本機伺服器開啟（例如 VSCode Live Server）。'
            : '';
        const err = vocabularyLoadError ? `\n\n錯誤：${vocabularyLoadError.message || vocabularyLoadError}` : '';
        alert(baseMsg + hint + err);
        return;
    }

    // 如果沒有選擇聲母，提醒使用者
    if (!targetInitial) {
        alert("請先選擇一個注音聲母！");
        return;
    }

    // 顯示載入中訊息
    const container = document.getElementById('gridContainer');
    const noResultMsg = document.getElementById('noResult');
    container.innerHTML = '';
    noResultMsg.style.display = 'none';
    
    const loadingMsg = document.createElement('div');
    loadingMsg.id = 'loadingMsg';
    loadingMsg.style.cssText = 'text-align: center; padding: 20px; color: #666;';
    loadingMsg.textContent = '搜尋中...';
    container.appendChild(loadingMsg);

    // 使用 setTimeout 確保 UI 更新
    setTimeout(() => {
        // 解析 positionType (例如 "2-1" 代表 2音節, 第1字)
        const [syllablesCount, targetPos] = positionType.split('-');
        const targetIndex = parseInt(targetPos) - 1; // 轉為 0-based index

        // 2. 篩選資料
        const results = vocabularyDB.filter(item => {
            return item.initial === targetInitial &&
                item.syllables == syllablesCount &&
                item.targetIndex == targetIndex;
        });

        // 移除載入訊息
        const loading = document.getElementById('loadingMsg');
        if (loading) loading.remove();

        // 3. 顯示結果
        renderResults(results);
    }, 100);
}

// 觸發 Unsplash 下載統計
function triggerUnsplashDownload(photoId) {
    // 使用 Unsplash API 觸發下載統計
    fetch(`https://api.unsplash.com/photos/${photoId}/download?client_id=hB2e4eye8zsvrifF6BG3ryQJhjasDpKe26fUqc4w6kI`)
        .then(response => response.json())
        .then(data => {
            console.log('Unsplash 下載統計已觸發:', data.url);
        })
        .catch(error => {
            console.warn('觸發 Unsplash 下載統計失敗:', error);
        });
}

// --- 渲染畫面邏輯 ---
function renderResults(data) {
    const container = document.getElementById('gridContainer');
    const noResultMsg = document.getElementById('noResult');

    const existingResultCountMsg = document.getElementById('resultCountMsg');
    if (existingResultCountMsg) {
        existingResultCountMsg.remove();
    }

    // 清空上次結果
    container.innerHTML = '';

    if (data.length === 0) {
        noResultMsg.textContent = "沒有找到符合條件的詞彙，請嘗試其他組合。";
        noResultMsg.style.display = 'block';
        return;
    } else {
        noResultMsg.style.display = 'none';
    }

    // 限制只顯示前 30 筆結果
    const displayData = data.slice(0, 30);
    const resultCountMsg = document.createElement('p');
    resultCountMsg.id = 'resultCountMsg';
    resultCountMsg.style.color = '#666';
    resultCountMsg.textContent = `搜尋結果：共 ${data.length} 筆詞彙，顯示前 ${displayData.length} 筆`;
    container.parentElement.insertBefore(resultCountMsg, container);

    // 產生卡片
    displayData.forEach(item => {
        // 建立卡片 div
        const card = document.createElement('div');
        card.className = 'card';

        // 圖片：優先使用資料庫中的 imageUrl (Wikimedia)
        let imageUrl = item.imageUrl;
        if (!imageUrl) {
            imageUrl = window.localImageManager.getImagePath(item.text);
        }
        const img = document.createElement('img');
        img.src = imageUrl;
        img.alt = item.text;
        img.loading = 'lazy';
        
        img.onerror = function() {
            // 如果圖片載入失敗，使用 HTML5 Canvas 動態生成帶有中文的佔位圖片
            const canvas = document.createElement('canvas');
            canvas.width = 150;
            canvas.height = 150;
            const ctx = canvas.getContext('2d');
            
            // 繪製綠色背景
            ctx.fillStyle = '#4CAF50';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // 繪製白色文字
            ctx.fillStyle = '#FFFFFF';
            // 使用系統原生中文字體，保證不亂碼
            ctx.font = 'bold 36px "PingFang TC", "Microsoft JhengHei", "Heiti TC", sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(item.text, canvas.width / 2, canvas.height / 2);
            
            // 將 Canvas 轉換為 Base64 圖片並設定為 src
            this.src = canvas.toDataURL('image/jpeg', 0.8);
            // 移除 onerror 避免無窮迴圈
            this.onerror = null;
        };

        // 文字標籤
        const textLabel = document.createElement('div');
        textLabel.className = 'text';
        textLabel.textContent = item.text;

        // 組合元素
        card.appendChild(img);
        card.appendChild(textLabel);
        
        // 添加點擊事件，顯示詞彙詳細資訊
        card.addEventListener('click', () => {
            const syllableText = item.syllables === 2 ? '雙音節' : '三音節';
            const positionText = ['第一', '第二', '第三'][item.targetIndex] + '個音節';
            const message = `詞彙：${item.text}\n聲母：${item.initial}\n音節：${syllableText}\n位置：${positionText}`;
            
            // 創建一個更美觀的提示框
            const modal = document.createElement('div');
            modal.style.cssText = `
                position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
                background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                z-index: 1000; max-width: 300px; text-align: center;
            `;
            modal.innerHTML = `
                <h3 style="margin: 0 0 15px 0; color: #333;">${item.text}</h3>
                <p style="margin: 5px 0; color: #666;">聲母：<strong>${item.initial}</strong></p>
                <p style="margin: 5px 0; color: #666;">音節：<strong>${syllableText}</strong></p>
                <p style="margin: 5px 0; color: #666;">位置：<strong>${positionText}</strong></p>
                <button onclick="this.parentElement.remove(); document.getElementById('overlay').remove();" 
                        style="margin-top: 15px; padding: 8px 16px; background: #4CAF50; color: white; 
                               border: none; border-radius: 4px; cursor: pointer;">關閉</button>
            `;
            
            // 添加遮罩層
            const overlay = document.createElement('div');
            overlay.id = 'overlay';
            overlay.style.cssText = `
                position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                background: rgba(0,0,0,0.5); z-index: 999;
            `;
            overlay.onclick = () => {
                modal.remove();
                overlay.remove();
            };
            
            document.body.appendChild(overlay);
            document.body.appendChild(modal);
        });
        
        // 添加滑鼠懸停效果
        card.style.cursor = 'pointer';
        
        container.appendChild(card);
    });
}