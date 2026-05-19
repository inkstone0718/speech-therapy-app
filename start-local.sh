#!/bin/bash

# 語言治療應用 - 本地啟動腳本

echo "🗣️ 語言治療詞彙練習系統"
echo "=================================="

# 檢查 Python 是否安裝
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安裝，請先安裝 Python3"
    echo "📖 安裝指南：https://www.python.org/downloads/"
    exit 1
fi

# 檢查是否在正確目錄
if [ ! -f "index.html" ]; then
    echo "❌ 請在專案根目錄執行此腳本"
    exit 1
fi

# 設定端口
PORT=8080

echo "✅ Python3 已安裝"
echo "📁 專案目錄：$(pwd)"
echo "🌐 啟動本地伺服器..."
echo "📱 請在瀏覽器中開啟："
echo ""
echo "🔗 http://localhost:$PORT"
echo ""

# 啟動伺服器
python3 -m http.server $PORT
