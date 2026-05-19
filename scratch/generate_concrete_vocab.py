import os
import json
import urllib.request
import urllib.parse
import ssl
import zhconv
from pypinyin import pinyin, Style

ssl._create_default_https_context = ssl._create_unverified_context

INITIALS = list("ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙ")

# Suffixes indicating abstract concepts or organization/people titles
ABSTRACT_SUFFIXES = (
    '性', '化', '度', '力', '制', '式', '法', '率', '型', '點', '線', '面', '體', '學', 
    '員', '官', '會', '局', '處', '部', '義', '期', '界', '科', '家', '事', '情', '態', 
    '感', '想', '觀', '論', '度', '者', '心', '主義', '制', '系', '風', '潮', '派', '流',
    '代', '段', '紀', '元', '朝', '限', '額', '差', '商', '業', '產', '政', '法', '律',
    '規', '章', '條', '款', '項', '目', '標', '的', '旨', '意', '義', '理', '教', '育',
    '文', '史', '地', '區', '域', '領', '土', '途', '徑', '方', '式', '模', '範', '結',
    '構', '組', '織', '機', '構', '團', '體', '社', '門', '室', '股', '組', '班', '級',
    '處', '所', '力', '心', '生', '士', '團', '長', '值', '作', '源', '本', '質', '額',
    '單', '數', '量'
)

# A massive list of child-friendly concrete nouns
CHILD_WORDS = [
    # Animals & Insects
    "貓咪", "小狗", "兔子", "老鼠", "大象", "獅子", "老虎", "長頸鹿", "斑馬", "袋鼠",
    "熊貓", "松鼠", "猴子", "綿羊", "山羊", "河馬", "犀牛", "狐狸", "野狼", "梅花鹿",
    "刺蝟", "無尾熊", "企鵝", "海豚", "鯨魚", "鯊魚", "海龜", "螃蟹", "龍蝦", "章魚",
    "海星", "水母", "青蛙", "烏龜", "蜥蜴", "恐龍", "小鳥", "老鷹", "貓頭鷹", "鸚鵡",
    "鴿子", "鴨子", "天鵝", "公雞", "母雞", "小雞", "孔雀", "燕子", "蝙蝠", "蝴蝶",
    "蜜蜂", "蜻蜓", "螞蟻", "蜘蛛", "蝸牛", "毛毛蟲", "蚊子", "蒼蠅", "金魚", "昆蟲",
    "壁虎", "瓢蟲", "蠶寶寶",
    # Food & Fruits & Vegetables
    "蘋果", "香蕉", "葡萄", "草莓", "西瓜", "芒果", "木瓜", "鳳梨", "橘子", "柳丁",
    "櫻桃", "芭樂", "荔枝", "椰子", "檸檬", "番茄", "胡蘿蔔", "南瓜", "茄子", "玉米",
    "馬鈴薯", "洋蔥", "青椒", "花椰菜", "香菇", "白菜", "菠菜", "大蒜", "辣椒", "豆腐",
    "雞蛋", "麵包", "蛋糕", "餅乾", "布丁", "巧克力", "糖果", "冰淇淋", "冰棒", "漢堡",
    "薯條", "披薩", "三明治", "熱狗", "包子", "饅頭", "水餃", "燒賣", "麵條", "壽司",
    "飯糰", "牛奶", "果汁", "汽水", "起司", "排骨", "烤肉", "貢丸", "肉丸", "茶葉",
    # Household Items & Furniture
    "桌子", "椅子", "沙發", "床鋪", "棉被", "枕頭", "衣櫃", "書架", "鞋櫃", "電視",
    "電腦", "冰箱", "洗衣機", "冷氣", "電風扇", "檯燈", "時鐘", "鏡子", "梳子", "吹風機",
    "牙刷", "牙膏", "毛巾", "肥皂", "垃圾桶", "掃把", "拖把", "衣架", "鑰匙", "雨傘",
    "杯子", "碗公", "盤子", "筷子", "湯匙", "叉子", "鍋子", "烤箱", "微波爐", "熱水瓶",
    "電話", "手電筒", "插座", "水龍頭", "洗手台", "浴缸", "馬桶", "地毯", "花瓶",
    # Clothing & Accessories
    "衣服", "褲子", "裙子", "洋裝", "外套", "毛衣", "襯衫", "T恤", "睡衣", "內衣",
    "內褲", "襪子", "鞋子", "靴子", "涼鞋", "雨鞋", "帽子", "手套", "圍巾", "皮帶",
    "眼鏡", "口罩", "手錶", "書包", "背包", "錢包", "項鍊", "手鍊", "戒指", "耳環",
    "髮夾", "雨衣", "泳衣",
    # Vehicles & Transportation
    "汽車", "公車", "卡車", "機車", "腳踏車", "火車", "高鐵", "捷運", "飛機", "直升機",
    "輪船", "帆船", "潛水艇", "火箭", "太空船", "救護車", "消防車", "警車", "計程車",
    "挖土機", "推土機", "垃圾車", "熱氣球", "雪橇", "馬車", "三輪車", "滑板車", "直排輪",
    "纜車", "水泥車", "吊車", "油罐車",
    # Nature & Outdoor Elements
    "太陽", "月亮", "星星", "彩虹", "白雲", "雨滴", "雪花", "閃電", "高山", "森林",
    "樹木", "樹葉", "花朵", "草地", "石頭", "沙子", "泥土", "河流", "湖泊", "海洋",
    "海灘", "貝殼", "火山", "瀑布", "公園", "花園", "操場", "鞦韆", "溜滑梯", "沙坑",
    "大樹", "向日葵", "玫瑰花", "蒲公英",
    # School & Office & Toys
    "課本", "故事書", "筆記本", "鉛筆", "蠟筆", "彩色筆", "原子筆", "橡皮擦", "尺", "剪刀",
    "膠水", "膠帶", "書桌", "書櫃", "黑板", "白板", "地球儀", "地圖", "書籤", "書夾",
    "玩具", "洋娃娃", "積木", "拼圖", "氣球", "風箏", "皮球", "籃球", "足球", "棒球",
    "羽毛球", "桌球", "溜溜球", "陀螺", "鋼琴", "吉他", "爵士鼓", "小提琴", "喇叭",
    "笛子", "鈴鐺", "沙鈴", "三角鐵", "黏土", "水彩", "畫架",
    # Body Parts & People Roles
    "眼睛", "鼻子", "耳朵", "嘴巴", "牙齒", "舌頭", "頭髮", "臉頰", "脖子", "肩膀",
    "手臂", "手指", "手掌", "手肘", "肚子", "屁股", "大腿", "膝蓋", "雙腳", "腳趾",
    "爸爸", "媽媽", "爺爺", "奶奶", "外公", "外婆", "哥哥", "姐姐", "弟弟", "妹妹",
    "老師", "醫生", "護士", "警察", "消防員", "郵差", "司機", "廚師", "太空人", "國王",
    "皇后", "公主", "王子", "小丑", "超人", "怪獸", "機器人", "仙女", "巫婆", "農夫",
    "漁夫", "廚師", "畫家", "歌手",
    # Specific difficult initials helper words (ㄗ, ㄘ, ㄙ, ㄓ, ㄔ, ㄕ, ㄖ)
    "自行車", "粽子", "紫菜", "字母", "草地", "草莓", "廁所", "瓷磚", "磁鐵", "司機",
    "絲巾", "寺廟", "索道", "掃把", "蜘蛛", "針筒", "紙巾", "珍珠", "竹筍", "指甲",
    "針線", "車子", "襯衫", "叉子", "翅膀", "抽屜", "城堡", "操場", "獅子", "手機",
    "手錶", "梳子", "書包", "樹木", "樹葉", "石頭", "蔬菜", "肉豬", "熱狗", "日曆",
    "日記", "熱氣球", "日光燈", "軟糖", "肉乾", "肉丸", "肉排", "皮球", "蘋果",
    "螃蟹", "披薩", "拼圖", "排骨", "皮帶", "皮鞋", "皮夾", "皮包", "瀑布", "跑車",
    "葡萄", "瓢蟲", "盆栽", "泡沫", "啤酒"
]

def get_bopomofo_initial(char):
    bopo = pinyin(char, style=Style.BOPOMOFO)[0][0]
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
    
    # 1. Prioritize our hand-crafted child concrete words (super high freq score)
    for w in CHILD_WORDS:
        words.append((w, 99999999))
        
    # 2. Add common nouns from jieba dict
    for line in lines:
        parts = line.strip().split(' ')
        if len(parts) >= 3:
            word = parts[0]
            freq = int(parts[1])
            pos = parts[2]
            
            # Strict POS filter: only common nouns 'n' (not nr, ns, nt, nz, vn)
            if pos == 'n':
                tc_word = zhconv.convert(word, 'zh-tw')
                # Filter out abstract suffixes AFTER conversion to Traditional Chinese
                if any(tc_word.endswith(suffix) for suffix in ABSTRACT_SUFFIXES):
                    continue
                # Length must be 2 or 3
                if len(tc_word) not in [2, 3]:
                    continue
                # Filter out non-Chinese
                if all('\u4e00' <= c <= '\u9fff' for c in tc_word):
                    words.append((tc_word, freq))
    
    # Sort by frequency descending (prioritizes hand-selected words, then standard high-frequency nouns)
    words.sort(key=lambda x: x[1], reverse=True)
    
    seen = set()
    unique_words = []
    for w, f in words:
        if w not in seen:
            seen.add(w)
            unique_words.append(w)
            
    return unique_words

def main():
    words = load_jieba_dict()
    print(f"Loaded {len(words)} unique Chinese common nouns.")
    
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
    print("Selecting 20 concrete words for each combination...")
    for init in INITIALS:
        for length in [2, 3]:
            for pos in range(length):
                pool = combinations[init][length][pos]
                
                if len(pool) == 0:
                    # Absolute emergency fallback if a category has no match
                    pool = ["蘋果", "香蕉", "貓咪", "大象"]
                
                selected = pool[:20]
                while len(selected) < 20:
                    selected.append(selected[0])
                
                for w in selected:
                    final_vocab.append({
                        "text": w,
                        "initial": init,
                        "syllables": length,
                        "targetIndex": pos
                    })
                    
    print(f"Generated {len(final_vocab)} items.")
    
    # Save to preview
    with open("preview_vocab.json", "w", encoding="utf-8") as f:
        json.dump({"vocabulary": final_vocab}, f, ensure_ascii=False, indent=2)
    print("Saved preview to preview_vocab.json")

if __name__ == "__main__":
    main()
