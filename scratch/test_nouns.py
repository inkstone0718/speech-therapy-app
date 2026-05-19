import urllib.request
import json
import ssl
import zhconv
from pypinyin import pinyin, Style

ssl._create_default_https_context = ssl._create_unverified_context

url = "https://raw.githubusercontent.com/fxsjy/jieba/master/extra_dict/dict.txt.big"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
print("Downloading dictionary...")
response = urllib.request.urlopen(req)
lines = response.read().decode('utf-8').split('\n')

abstract_suffixes = ('性', '化', '度', '力', '制', '式', '法', '率', '型', '點', '線', '面', '體', '學', '員', '官', '會', '局', '處', '部', '義', '期', '界', '科', '家', '事', '情', '態', '感', '想', '觀', '論', '度', '者', '心')

words = []
for line in lines:
    parts = line.strip().split(' ')
    if len(parts) >= 3:
        word = parts[0]
        freq = int(parts[1])
        pos = parts[2]
        
        # Strict POS filter: only common nouns 'n' (not nr, ns, nt, nz)
        if pos == 'n':
            # Child friendly: avoid abstract suffixes
            if any(word.endswith(suffix) for suffix in abstract_suffixes):
                continue
            if all('\u4e00' <= c <= '\u9fff' for c in word):
                tc_word = zhconv.convert(word, 'zh-tw')
                words.append((tc_word, freq))

# Print top 100
words.sort(key=lambda x: x[1], reverse=True)
print("Top 50 words:")
for w, f in words[:50]:
    print(f"{w} ({f})")
