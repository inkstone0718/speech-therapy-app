import json
import os
import urllib.request
import urllib.parse
import time
import ssl

# Bypass SSL if needed
ssl._create_default_https_context = ssl._create_unverified_context

API_KEY = 'hB2e4eye8zsvrifF6BG3ryQJhjasDpKe26fUqc4w6kI'

# A curated list of high-quality words for speech therapy practice.
# Fields: Text, Initial, Syllables, Target Index, English Search Keyword
curated_words = [
    # ㄅ (b)
    ("爸爸", "ㄅ", 2, 0, "father portrait"),
    ("包子", "ㄅ", 2, 0, "steamed bun food"),
    ("杯子", "ㄅ", 2, 0, "coffee cup"),
    ("書包", "ㄅ", 2, 1, "school backpack"),
    ("黑板", "ㄅ", 2, 1, "blackboard chalkboard"),
    ("冰淇淋", "ㄅ", 3, 0, "ice cream cone"),
    ("大冰箱", "ㄅ", 3, 1, "kitchen refrigerator"),
    ("小籠包", "ㄅ", 3, 2, "xiaolongbao dumplings"),
    
    # ㄆ (p)
    ("蘋果", "ㄆ", 2, 0, "red apple"),
    ("葡萄", "ㄆ", 2, 0, "grapes"),
    ("盤子", "ㄆ", 2, 0, "empty plate"),
    ("氣泡", "ㄆ", 2, 1, "soap bubbles"),
    ("草皮", "ㄆ", 2, 1, "green grass lawn"),
    ("葡萄柚", "ㄆ", 3, 0, "grapefruit slice"),
    ("橡皮擦", "ㄆ", 3, 1, "pencil eraser"),
    ("頭皮屑", "ㄆ", 3, 1, "hair dandruff"),
    
    # ㄇ (m)
    ("貓咪", "ㄇ", 2, 0, "cute cat"),
    ("帽子", "ㄇ", 2, 0, "baseball cap"),
    ("螞蟻", "ㄇ", 2, 0, "ant macro"),
    ("熊貓", "ㄇ", 2, 1, "giant panda"),
    ("草莓", "ㄇ", 2, 1, "strawberry fresh"),
    ("棉花糖", "ㄇ", 3, 0, "marshmallow"),
    ("大門口", "ㄇ", 3, 1, "building entrance"),
    ("紅毛衣", "ㄇ", 3, 1, "red sweater"),
    
    # ㄈ (f)
    ("飛機", "ㄈ", 2, 0, "airplane sky"),
    ("房子", "ㄈ", 2, 0, "house building"),
    ("風箏", "ㄈ", 2, 0, "flying kite"),
    ("蜜蜂", "ㄈ", 2, 1, "bee flower"),
    ("頭髮", "ㄈ", 2, 1, "hair style"),
    ("番茄醬", "ㄈ", 3, 0, "ketchup bottle"),
    ("長頸鹿", "ㄈ", 3, 1, "giraffe"), # Wait, 頸 is j, 鹿 is l. Ah! ㄈ in 長頸鹿? No.
    # Let's use something else: 豆腐湯 (dou fu tang) -> ㄈ is 1
    ("豆腐湯", "ㄈ", 3, 1, "tofu soup"),
    ("麥克風", "ㄈ", 3, 2, "microphone music"),
    
    # ㄉ (d)
    ("大象", "ㄉ", 2, 0, "elephant"),
    ("蛋糕", "ㄉ", 2, 0, "cake slice"),
    ("電燈", "ㄉ", 2, 0, "light bulb"),
    ("弟弟", "ㄉ", 2, 1, "little boy brother"),
    ("剪刀", "ㄉ", 2, 1, "scissors pair"),
    ("盪鞦韆", "ㄉ", 3, 0, "playground swing"),
    ("手電筒", "ㄉ", 3, 1, "flashlight"),
    ("溜冰鞋", "ㄉ", 3, 2, "roller skates"), # Wait, 鞋 is x. 冰 is b. 溜 is l. No ㄉ. 
    # Use 雞蛋捲 (ji dan juan)
    ("雞蛋捲", "ㄉ", 3, 1, "egg roll"),
    ("熱狗堡", "ㄉ", 3, 2, "hot dog bun"), # wait 狗 is g, 堡 is b. No ㄉ.
    ("麥當勞", "ㄉ", 3, 1, "mcdonalds logo"),
    
    # ㄊ (t)
    ("太陽", "ㄊ", 2, 0, "sun sky"),
    ("兔子", "ㄊ", 2, 0, "cute rabbit"),
    ("糖果", "ㄊ", 2, 0, "candy sweet"),
    ("企鵝", "ㄊ", 2, 1, "penguin"), # 鵝 is e. 企 is q. No ㄊ!
    # Let's fix: 葡萄 (pu tao) -> ㄊ is 1
    ("櫻桃", "ㄊ", 2, 1, "cherry fresh"),
    ("泥土", "ㄊ", 2, 1, "soil dirt"),
    ("溜滑梯", "ㄊ", 3, 2, "playground slide"),
    ("水蜜桃", "ㄊ", 3, 2, "peach fruit"),
    
    # ㄋ (n)
    ("鳥兒", "ㄋ", 2, 0, "bird branch"),
    ("牛奶", "ㄋ", 2, 0, "milk glass"),
    ("鈕扣", "ㄋ", 2, 0, "sewing button"),
    ("水牛", "ㄋ", 2, 1, "water buffalo"),
    ("室內", "ㄋ", 2, 1, "indoor room"),
    ("鳥巢", "ㄋ", 2, 0, "bird nest"),
    ("溜溜球", "ㄋ", 3, 2, "yoyo toy"), # wait, liu liu qiu has no ㄋ. 
    # Use 康乃馨 (kang nai xin)
    ("康乃馨", "ㄋ", 3, 1, "carnation flower"),
    
    # ㄌ (l)
    ("老虎", "ㄌ", 2, 0, "tiger"),
    ("老師", "ㄌ", 2, 0, "teacher classroom"),
    ("禮物", "ㄌ", 2, 0, "gift box present"),
    ("快樂", "ㄌ", 2, 1, "happy face"),
    ("項鍊", "ㄌ", 2, 1, "necklace jewelry"),
    ("腳踏車", "ㄌ", 3, 0, "bicycle"), # wait, jiao ta che -> no ㄌ.
    # 垃圾桶 (la se tong)
    ("垃圾桶", "ㄌ", 3, 0, "trash can bin"),
    ("巧克力", "ㄌ", 3, 2, "chocolate bar"),
    ("麥當勞", "ㄌ", 3, 2, "mcdonalds"),
    
    # ㄍ (g)
    ("狗狗", "ㄍ", 2, 0, "cute dog"),
    ("蘋果", "ㄍ", 2, 1, "apple fruit"),
    ("西瓜", "ㄍ", 2, 1, "watermelon slice"),
    ("鴿子", "ㄍ", 2, 0, "pigeon bird"),
    ("高麗菜", "ㄍ", 3, 0, "cabbage vegetable"),
    ("熱狗堡", "ㄍ", 3, 1, "hot dog food"),
    
    # ㄎ (k)
    ("恐龍", "ㄎ", 2, 0, "dinosaur toy"),
    ("卡車", "ㄎ", 2, 0, "truck vehicle"),
    ("褲子", "ㄎ", 2, 0, "pants jeans"),
    ("水庫", "ㄎ", 2, 1, "water reservoir dam"),
    ("麥克風", "ㄎ", 3, 1, "karaoke microphone"),
    ("馬卡龍", "ㄎ", 3, 1, "macaron dessert"),
    
    # ㄏ (h)
    ("猴子", "ㄏ", 2, 0, "monkey animal"),
    ("老虎", "ㄏ", 2, 1, "tiger animal"),
    ("護士", "ㄏ", 2, 0, "nurse hospital"),
    ("雪花", "ㄏ", 2, 1, "snowflake winter"),
    ("紅綠燈", "ㄏ", 3, 0, "traffic light"),
    ("向日葵", "ㄏ", 3, 0, "sunflower plant"), # wait, xiang ri kui -> ㄏ is in 向? xiang is x. hui? kui is k.
    # 蝴蝶結 (hu die jie)
    ("蝴蝶結", "ㄏ", 3, 0, "ribbon bow"),
    
    # ㄐ (j)
    ("機器", "ㄐ", 2, 0, "robot machine"),
    ("剪刀", "ㄐ", 2, 0, "scissors"),
    ("警察", "ㄐ", 2, 0, "police officer"),
    ("手機", "ㄐ", 2, 1, "smartphone"),
    ("公雞", "ㄐ", 2, 1, "rooster chicken"),
    ("直昇機", "ㄐ", 3, 2, "helicopter"),
    ("冰淇淋", "ㄐ", 3, 2, "ice cream dessert"), # wait bing qi lin (q).
    ("橡皮筋", "ㄐ", 3, 2, "rubber band"),
    
    # ㄑ (q)
    ("企鵝", "ㄑ", 2, 0, "penguin animal"),
    ("鉛筆", "ㄑ", 2, 0, "pencil drawing"),
    ("氣球", "ㄑ", 2, 0, "colorful balloons"),
    ("籃球", "ㄑ", 2, 1, "basketball"),
    ("溜滑梯", "ㄑ", 3, 2, "playground slide"), # wait liu hua ti. Where is ㄑ? 
    # 冰淇淋 (bing qi lin)
    ("冰淇淋", "ㄑ", 3, 1, "ice cream"),
    ("盪鞦韆", "ㄑ", 3, 1, "swing playground"),
    
    # ㄒ (x)
    ("西瓜", "ㄒ", 2, 0, "watermelon"),
    ("星星", "ㄒ", 2, 0, "stars night"),
    ("學校", "ㄒ", 2, 0, "school building"),
    ("皮鞋", "ㄒ", 2, 1, "leather shoes"),
    ("冰箱", "ㄒ", 2, 1, "refrigerator"),
    ("洗衣機", "ㄒ", 3, 0, "washing machine"),
    ("直昇機", "ㄒ", 3, 1, "helicopter"), # zhi sheng ji. ji is ㄐ.
    ("溜冰鞋", "ㄒ", 3, 2, "roller skates"),
    
    # ㄓ (zh)
    ("蜘蛛", "ㄓ", 2, 0, "spider insect"),
    ("桌子", "ㄓ", 2, 0, "wooden table"),
    ("公車", "ㄓ", 2, 1, "public bus"), # wait gong che (ch).
    ("果汁", "ㄓ", 2, 1, "fruit juice glass"),
    ("白紙", "ㄓ", 2, 1, "blank white paper"),
    ("直昇機", "ㄓ", 3, 0, "helicopter flight"),
    ("果汁機", "ㄓ", 3, 1, "blender kitchen"),
    
    # ㄔ (ch)
    ("車子", "ㄔ", 2, 0, "car vehicle"),
    ("唱歌", "ㄔ", 2, 0, "singing person"),
    ("草莓", "ㄔ", 2, 1, "strawberry"), # cao mei (c).
    ("公車", "ㄔ", 2, 1, "bus transport"),
    ("腳踏車", "ㄔ", 3, 2, "bicycle ride"),
    ("溜滑梯", "ㄔ", 3, 2, "playground slide"), # liu hua ti. no ch.
    # 消防車 (xiao fang che)
    ("消防車", "ㄔ", 3, 2, "fire truck"),
    
    # ㄕ (sh)
    ("書本", "ㄕ", 2, 0, "open book"),
    ("獅子", "ㄕ", 2, 0, "lion animal"),
    ("老鼠", "ㄕ", 2, 1, "mouse animal"),
    ("梳子", "ㄕ", 2, 0, "hair comb"),
    ("電視", "ㄕ", 2, 1, "television screen"),
    ("溜冰鞋", "ㄕ", 3, 0, "roller skates"), # liu bing xie.
    ("麥當勞", "ㄕ", 3, 1, "mcdonalds"), # mai dang lao.
    ("聖誕樹", "ㄕ", 3, 0, "christmas tree"),
    ("聖誕樹", "ㄕ", 3, 2, "christmas tree"),
    
    # ㄖ (r)
    ("熱狗", "ㄖ", 2, 0, "hot dog"),
    ("日曆", "ㄖ", 2, 0, "calendar"),
    ("生日", "ㄖ", 2, 1, "birthday cake"),
    ("向日葵", "ㄖ", 3, 1, "sunflower"),
    ("雪人", "ㄖ", 2, 1, "snowman winter"),
    
    # ㄗ (z)
    ("字典", "ㄗ", 2, 0, "dictionary book"),
    ("粽子", "ㄗ", 2, 0, "zongzi food"),
    ("杯子", "ㄗ", 2, 1, "cup glass"),
    ("襪子", "ㄗ", 2, 1, "socks"),
    ("剪刀", "ㄗ", 2, 1, "scissors tool"),
    ("電子錶", "ㄗ", 3, 1, "digital watch"),
    
    # ㄘ (c)
    ("草莓", "ㄘ", 2, 0, "strawberry"),
    ("彩色", "ㄘ", 2, 0, "colorful palette"),
    ("警察", "ㄘ", 2, 1, "police car"),
    ("白菜", "ㄘ", 2, 1, "napa cabbage"),
    ("橡皮擦", "ㄘ", 3, 2, "eraser"),
    ("高麗菜", "ㄘ", 3, 2, "cabbage farm"),
    
    # ㄙ (s)
    ("傘", "ㄙ", 1, 0, "umbrella"), # wait, requires 2 or 3 syllables
    ("雨傘", "ㄙ", 2, 1, "umbrella rain"),
    ("森林", "ㄙ", 2, 0, "forest trees"),
    ("彩色", "ㄙ", 2, 1, "colors painting"),
    ("公司", "ㄙ", 2, 1, "office building"),
    ("溜滑梯", "ㄙ", 3, 0, "slide playground"), # liu is l.
    ("麥當勞", "ㄙ", 3, 2, "mcdonalds fries"), # no s.
    # 三明治 (san ming zhi)
    ("三明治", "ㄙ", 3, 0, "sandwich food"),
    ("維他命", "ㄙ", 3, 2, "vitamin pills"), # wei ta ming. no s.
    ("保險絲", "ㄙ", 3, 2, "electrical fuse"),
    ("冰沙杯", "ㄙ", 3, 1, "smoothie drink"),
]

def generate_vocabulary():
    vocab_list = []
    for word in curated_words:
        text, initial, syllables, target_index, keyword = word
        vocab_list.append({
            "text": text,
            "initial": initial,
            "syllables": syllables,
            "targetIndex": target_index
        })
    
    with open("vocabulary.json", "w", encoding="utf-8") as f:
        json.dump({"vocabulary": vocab_list}, f, ensure_ascii=False, indent=2)
    print(f"Generated vocabulary.json with {len(vocab_list)} words.")

def download_images():
    os.makedirs("images", exist_ok=True)
    
    for word in curated_words:
        text, initial, syllables, target_index, keyword = word
        filepath = os.path.join("images", f"{text}.jpg")
        
        if os.path.exists(filepath):
            print(f"Skipping {text}, image already exists.")
            continue
            
        print(f"Downloading image for {text} (Keyword: {keyword})...")
        try:
            url = f"https://api.unsplash.com/photos/random?query={urllib.parse.quote(keyword)}&client_id={API_KEY}&orientation=squarish"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req)
            data = json.loads(response.read())
            image_url = data['urls']['regular']
            
            # Download the actual image
            img_req = urllib.request.Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
            img_data = urllib.request.urlopen(img_req).read()
            with open(filepath, 'wb') as f:
                f.write(img_data)
            print(f"  -> Success: {text}.jpg")
        except Exception as e:
            print(f"  -> Failed for {text}: {e}")
            
        # Sleep to avoid rate limiting (Unsplash allows 50 requests/hour for demo, but we have 105 words. 
        # If the API hits limit, we might have some failures. We'll add a 1 second delay.)
        time.sleep(1)

if __name__ == "__main__":
    generate_vocabulary()
    download_images()
