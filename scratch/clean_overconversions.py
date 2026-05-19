import json

REPLACEMENTS = {
    "裡程碑": "里程碑",
    "石灰巖": "石灰岩",
    "碎屑巖": "碎屑岩",
    "花崗巖": "花崗岩",
    "玄武巖": "玄武岩",
    "大理巖": "大理岩",
    "沉積巖": "沉積岩",
    "變質巖": "變質岩",
    "砂巖": "砂岩",
    "頁巖": "頁岩",
    "板巖": "板岩",
    "岩石巖": "岩石",
    "村裡人": "村里人",
    "私下裡": "私下里",
    "著色劑": "顏料" # Replace with a more child-friendly word
}

def main():
    try:
        with open("vocabulary_edit.json", "r", encoding="utf-8") as f:
            structured = json.load(f)
    except FileNotFoundError:
        print("vocabulary_edit.json not found.")
        return
        
    updated_count = 0
    for key, words in structured.items():
        new_words = []
        for word in words:
            original = word
            for bad, good in REPLACEMENTS.items():
                if bad in word:
                    word = word.replace(bad, good)
            if word != original:
                print(f"Fixed: {original} -> {word}")
                updated_count += 1
            new_words.append(word)
        structured[key] = new_words
        
    if updated_count > 0:
        with open("vocabulary_edit.json", "w", encoding="utf-8") as f:
            json.dump(structured, f, ensure_ascii=False, indent=2)
        print(f"Cleaned up {updated_count} words in vocabulary_edit.json.")
    else:
        print("No over-conversions found to clean.")

if __name__ == "__main__":
    main()
