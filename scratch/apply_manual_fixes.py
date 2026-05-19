import json

FIXES = {
    "ㄅ_3_2": {
        "發布權": "小背包"
    },
    "ㄆ_3_1": {
        "排洩物": "蘋果汁"
    },
    "ㄈ_3_2": {
        "衝鋒鎗": "小風車"
    },
    "ㄉ_3_3": {
        "遊擊隊": "小檯燈"
    },
    "ㄋ_3_1": {
        "泥灰巖": "牛奶糖"
    },
    "ㄌ_3_1": {
        "雷射器": "綠豆湯"
    },
    "ㄎ_3_2": {
        "準考證": "小口袋"
    },
    "ㄏ_3_3": {
        "心裡話": "爆米花"
    },
    "ㄐ_3_1": {
        "建築群": "金魚缸"
    },
    "ㄐ_3_2": {
        "遊擊隊": "小積木"
    },
    "ㄑ_3_3": {
        "建築群": "小氣球"
    },
    "ㄒ_3_3": {
        "嚴義壎": "小星星"
    },
    "ㄓ_3_2": {
        "建築群": "小蜘蛛"
    },
    "ㄓ_3_3": {
        "遊擊戰": "包裝紙",
        "準考證": "大珍珠"
    },
    "ㄔ_3_1": {
        "衝鋒鎗": "車輪胎"
    },
    "ㄖ_3_1": {
        "軟體園": "熱氣球"
    },
    "ㄙ_3_2": {
        "顏料": "調色盤"
    }
}

def main():
    try:
        with open("vocabulary_edit.json", "r", encoding="utf-8") as f:
            structured = json.load(f)
    except FileNotFoundError:
        print("vocabulary_edit.json not found.")
        return
        
    updated = 0
    for category, word_replacements in FIXES.items():
        if category in structured:
            words = structured[category]
            new_words = []
            for w in words:
                if w in word_replacements:
                    new_w = word_replacements[w]
                    print(f"Replacing in {category}: {w} -> {new_w}")
                    new_words.append(new_w)
                    updated += 1
                else:
                    new_words.append(w)
            structured[category] = new_words
            
    if updated > 0:
        with open("vocabulary_edit.json", "w", encoding="utf-8") as f:
            json.dump(structured, f, ensure_ascii=False, indent=2)
        print(f"Applied {updated} manual fixes to vocabulary_edit.json.")
    else:
        print("No manual fixes were applied.")

if __name__ == "__main__":
    main()
