import json
import urllib.request
import urllib.parse
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed
from pypinyin import pinyin, Style

ssl._create_default_https_context = ssl._create_unverified_context

INITIALS = list("ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙ")

# Loaded from our child-friendly list
from generate_concrete_vocab import CHILD_WORDS

# Load Jieba dictionary for local verification
def load_jieba_set():
    url = "https://raw.githubusercontent.com/fxsjy/jieba/master/extra_dict/dict.txt.big"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    print("Downloading Jieba dictionary for validation...")
    try:
        response = urllib.request.urlopen(req)
        lines = response.read().decode('utf-8').split('\n')
        words = set()
        for line in lines:
            parts = line.strip().split(' ')
            if len(parts) > 0:
                words.add(parts[0])
        return words
    except Exception as e:
        print("Failed to download Jieba dictionary. Local verification will rely on CHILD_WORDS.")
        return set()

def check_moedict(word):
    # Check Moedict JSON API
    url = f"https://www.moedict.tw/a/{urllib.parse.quote(word)}.json"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=3) as response:
            if response.status == 200:
                return True
    except:
        pass
    return False

def get_bopomofo_initial(char):
    bopo = pinyin(char, style=Style.BOPOMOFO)[0][0]
    if len(bopo) > 0 and bopo[0] in INITIALS:
        return bopo[0]
    return ""

def main():
    print("Loading vocabulary_edit.json...")
    try:
        with open("vocabulary_edit.json", "r", encoding="utf-8") as f:
            structured = json.load(f)
    except FileNotFoundError:
        print("vocabulary_edit.json not found.")
        return
        
    jieba_set = load_jieba_set()
    child_set = set(CHILD_WORDS)
    
    issues = []
    
    # Gather all unique words to query Moedict asynchronously
    all_words = set()
    for words in structured.values():
        for w in words:
            all_words.add(w.strip())
            
    print(f"Verifying {len(all_words)} unique words...")
    
    # We only query Moedict for words NOT in our CHILD_WORDS or Jieba dict to save API requests
    api_words = [w for w in all_words if w not in child_set and w not in jieba_set]
    print(f"Checking {len(api_words)} words against Moedict online API...")
    
    moe_results = {}
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check_moedict, w): w for w in api_words}
        for future in as_completed(futures):
            w = futures[future]
            try:
                moe_results[w] = future.result()
            except:
                moe_results[w] = False
                
    # Now validate category-specific criteria
    for category, words in structured.items():
        parts = category.split("_")
        expected_init = parts[0]
        expected_syl = int(parts[1])
        expected_pos = int(parts[2]) - 1
        
        # Check size limit (exactly 20 words required)
        if len(words) != 20:
            issues.append(f"Category '{category}' must have exactly 20 words (currently has {len(words)}).")
            
        for i, word in enumerate(words):
            word = word.strip()
            if not word:
                issues.append(f"Category '{category}' index {i} is empty.")
                continue
                
            length = len(word)
            
            # 1. Validate length
            if length != expected_syl:
                issues.append(f"Category '{category}': Word '{word}' has length {length} (expected {expected_syl}).")
                continue
                
            # 2. Validate target pronunciation initial
            target_char = word[expected_pos]
            actual_init = get_bopomofo_initial(target_char)
            if actual_init != expected_init:
                issues.append(f"Category '{category}': Word '{word}' has initial '{actual_init}' at target position (expected '{expected_init}').")
                
            # 3. Validate word existence (acceptability)
            is_valid = (word in child_set) or (word in jieba_set) or moe_results.get(word, False)
            
            # If length is 3 and starts with a common prefix, check the 2-character root
            common_prefixes = ['大', '小', '老', '紅', '綠', '藍', '黃', '黑', '白', '新', '舊', '髒', '好', '壞', '真', '假', '多', '少', '長', '短', '高', '矮', '胖', '瘦', '熱', '冷', '車']
            common_suffixes = ['酥', '醬', '汁', '車', '糖', '包', '機', '球', '筆', '紙', '刀', '水', '油', '粉', '皮', '肉', '骨', '花']
            
            if not is_valid and length == 3:
                if word[0] in common_prefixes:
                    root_word = word[1:]
                    is_valid = (root_word in child_set) or (root_word in jieba_set) or check_moedict(root_word)
                elif word[-1] in common_suffixes:
                    root_word = word[:-1]
                    is_valid = (root_word in child_set) or (root_word in jieba_set) or check_moedict(root_word)
                
            if not is_valid:
                issues.append(f"Category '{category}': Word '{word}' is unrecognized (not found in seed list, Jieba dictionary, or Moedict). Possible typo!")
                
    if issues:
        print("\n=== Validation Failed! Found issues: ===")
        for issue in issues[:30]:
            print(f"- {issue}")
        if len(issues) > 30:
            print(f"... and {len(issues) - 30} more issues.")
        print("\nPlease fix the issues in vocabulary_edit.json and run the validation again.")
    else:
        print("\n=== Validation Successful! All words are acceptable and phonetically correct! ===")

if __name__ == "__main__":
    main()
