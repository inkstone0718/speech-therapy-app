import json
from pypinyin import pinyin, Style

INITIALS = list("ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙ")

def get_bopomofo_initial(char):
    bopo = pinyin(char, style=Style.BOPOMOFO)[0][0]
    if len(bopo) > 0 and bopo[0] in INITIALS:
        return bopo[0]
    return ""

def main():
    try:
        with open("vocabulary_edit.json", "r", encoding="utf-8") as f:
            structured = json.load(f)
    except FileNotFoundError:
        print("vocabulary_edit.json not found. Please make sure the file exists.")
        return
        
    flat_vocab = []
    
    for key, words in structured.items():
        parts = key.split("_")
        expected_init = parts[0]
        expected_syl = int(parts[1])
        expected_pos = int(parts[2]) - 1
        
        for word in words:
            # Clean up spacing
            word = word.strip()
            if not word:
                continue
                
            length = len(word)
            
            # Recalculate pinyin phonetics dynamically for safety
            char_to_check = word[expected_pos] if expected_pos < length else word[-1]
            actual_init = get_bopomofo_initial(char_to_check)
            
            # If the user changed the spelling entirely, warn them but keep it
            if actual_init != expected_init:
                print(f"Warning: Word '{word}' in category '{key}' actually has initial '{actual_init}' instead of '{expected_init}'.")
                
            flat_vocab.append({
                "text": word,
                "initial": expected_init, # Keep it in this category for training consistency
                "syllables": expected_syl,
                "targetIndex": expected_pos
            })
            
    print(f"Successfully processed {len(flat_vocab)} vocabulary items.")
    
    # Save back to vocabulary.json
    with open("vocabulary.json", "w", encoding="utf-8") as f:
        json.dump({"vocabulary": flat_vocab}, f, ensure_ascii=False, indent=2)
        
    print("Updated vocabulary.json! You can now run the image downloader to fetch images for these words.")

if __name__ == "__main__":
    main()
