import os
import json
import random
import urllib.request
import urllib.parse
import ssl
import zhconv
from concurrent.futures import ThreadPoolExecutor, as_completed
from pypinyin import pinyin, Style

ssl._create_default_https_context = ssl._create_unverified_context

INITIALS = list("ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙ")

def get_bopomofo_initial(char):
    # pinyin returns a list of lists, we take the first pronunciation
    bopo = pinyin(char, style=Style.BOPOMOFO)[0][0]
    # The initial is the first character if it is in INITIALS
    if len(bopo) > 0 and bopo[0] in INITIALS:
        return bopo[0]
    return ""

def load_jieba_dict():
    url = "https://raw.githubusercontent.com/fxsjy/jieba/master/extra_dict/dict.txt.big"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    print("Downloading Jieba dictionary...")
    response = urllib.request.urlopen(req)
    lines = response.read().decode('utf-8').split('\n')
    words = []
    for line in lines:
        parts = line.strip().split(' ')
        if len(parts) >= 3:
            word = parts[0]
            freq = int(parts[1])
            pos = parts[2]
            
            # Keep only nouns (n, nr, ns, nt, nz, etc)
            if pos.startswith('n'):
                # filter out non-chinese
                if all('\u4e00' <= c <= '\u9fff' for c in word):
                    # Convert to Traditional Chinese (zh-tw)
                    tc_word = zhconv.convert(word, 'zh-tw')
                    words.append((tc_word, freq))
    
    # Sort by frequency descending, so we get common words for kids
    words.sort(key=lambda x: x[1], reverse=True)
    
    # Remove duplicates but preserve order (highest freq first)
    seen = set()
    unique_words = []
    for w, f in words:
        if w not in seen:
            seen.add(w)
            unique_words.append(w)
            
    return unique_words

def fetch_image_url(word):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrsearch={urllib.parse.quote(word)}&gsrnamespace=6&gsrlimit=1&prop=imageinfo&iiprop=url"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 SpeechTherapyApp/1.0'})
    try:
        response = urllib.request.urlopen(req, timeout=5)
        data = json.loads(response.read())
        pages = data.get('query', {}).get('pages', {})
        if pages:
            # get the first page
            page_id = list(pages.keys())[0]
            image_url = pages[page_id]['imageinfo'][0]['url']
            return image_url
    except Exception as e:
        pass
    return None

def main():
    words = load_jieba_dict()
    print(f"Loaded {len(words)} Chinese words.")
    
    combinations = {}
    for init in INITIALS:
        combinations[init] = {
            2: {0: [], 1: []},
            3: {0: [], 1: [], 2: []}
        }
    
    print("Grouping words by initial and position...")
    for w in words:
        length = len(w)
        if length not in [2, 3]:
            continue
            
        for i, char in enumerate(w):
            init = get_bopomofo_initial(char)
            if init in INITIALS:
                if w not in combinations[init][length][i]:
                    combinations[init][length][i].append(w)
                
    final_vocab = []
    print("Selecting 20 words for each combination...")
    for init in INITIALS:
        for length in [2, 3]:
            for pos in range(length):
                pool = combinations[init][length][pos]
                # Take the top 20 most frequent words instead of random sample
                if len(pool) == 0:
                    pool = [f"無資料{init}"]
                
                selected = pool[:20]
                while len(selected) < 20:
                    # if not enough, repeat the most common ones
                    selected.append(selected[0])
                
                for w in selected:
                    final_vocab.append({
                        "text": w,
                        "initial": init,
                        "syllables": length,
                        "targetIndex": pos
                    })
                    
    print(f"Generated {len(final_vocab)} vocabulary items (105 combinations * 20 words).")
    
    print("Fetching image URLs from Wikimedia asynchronously...")
    def process_item(item):
        img_url = fetch_image_url(item["text"])
        item["imageUrl"] = img_url
        return item

    completed = 0
    total = len(final_vocab)
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(process_item, item): item for item in final_vocab}
        for future in as_completed(futures):
            completed += 1
            if completed % 100 == 0:
                print(f"Fetched {completed}/{total} images...")
                
    with open("vocabulary.json", "w", encoding="utf-8") as f:
        json.dump({"vocabulary": final_vocab}, f, ensure_ascii=False, indent=2)
    print("Done! Saved to vocabulary.json")

if __name__ == "__main__":
    main()
