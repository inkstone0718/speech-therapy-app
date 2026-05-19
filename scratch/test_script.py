from pypinyin import pinyin, Style
from duckduckgo_search import DDGS

word = "蘋果"
bopomofo = pinyin(word, style=Style.BOPOMOFO)
print(f"Bopomofo for {word}: {bopomofo}")

# Extract the initial sound (聲母)
# In pypinyin, Bopomofo style returns the whole bopomofo syllable. e.g. ㄆㄧㄥˊ, ㄍㄨㄛˇ
# We only want the first character if it's an initial.
initials = "ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙ"
for syl in bopomofo:
    first_char = syl[0][0]
    initial = first_char if first_char in initials else ""
    print(f"Syllable {syl[0]} -> Initial: {initial}")

try:
    results = DDGS().images(word, max_results=1)
    if results:
        print(f"Found image: {results[0]['image']}")
    else:
        print("No image found.")
except Exception as e:
    print(f"Search error: {e}")
