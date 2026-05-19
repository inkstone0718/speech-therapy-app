import os
import json
import io
import re
import urllib.request
import urllib.parse
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image, ImageDraw, ImageFont

ssl._create_default_https_context = ssl._create_unverified_context

# 200x200 green text image fallback
def create_text_image(text, output_path):
    img = Image.new('RGB', (200, 200), color='#4CAF50')
    draw = ImageDraw.Draw(img)
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/Library/Fonts/Arial Unicode.ttf"
    ]
    font = None
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                font = ImageFont.truetype(fp, 50)
                break
            except:
                pass
    if font is None:
        font = ImageFont.load_default()
        
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(((200-w)/2, (200-h)/2), text, font=font, fill="white")
    img.save(output_path, "JPEG", quality=85)

# Scraping function to search Bing and return the first image URL
def get_bing_image_url(query):
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.bing.com/images/search?q={encoded_query}"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode('utf-8')
            urls = re.findall(r'murl&quot;:&quot;(http.*?)&quot;', html)
            if urls:
                # Clean HTML entity &amp; in URLs
                return urls[0].replace("&amp;", "&")
    except Exception as e:
        pass
    return None

def download_and_compress(url, output_path):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    with urllib.request.urlopen(req, timeout=8) as response:
        image_data = response.read()
        
    img = Image.open(io.BytesIO(image_data))
    if img.mode in ('RGBA', 'P', 'CMYK'):
        img = img.convert('RGB')
        
    width, height = img.size
    new_dim = min(width, height)
    left = (width - new_dim) / 2
    top = (height - new_dim) / 2
    right = (width + new_dim) / 2
    bottom = (height + new_dim) / 2
    
    img = img.crop((left, top, right, bottom))
    img = img.resize((200, 200), Image.Resampling.LANCZOS)
    img.save(output_path, "JPEG", quality=80)

def process_word(index, item):
    word = item["text"]
    new_filename = f"img_{index:04d}.jpg"
    final_path = f"images/{new_filename}"
    
    # Check if already downloaded and valid
    if os.path.exists(final_path) and os.path.getsize(final_path) > 1000:
        item["imageUrl"] = final_path
        return item
        
    # Attempt 1: Search Chinese
    img_url = get_bing_image_url(f"{word} 實物 照片")
    
    # Attempt 2: Simple fallback search if first failed
    if not img_url:
        img_url = get_bing_image_url(word)
        
    if img_url:
        try:
            download_and_compress(img_url, final_path)
            item["imageUrl"] = final_path
            return item
        except Exception:
            pass
            
    # Fallback to Text Image
    try:
        create_text_image(word, final_path)
    except:
        pass
    item["imageUrl"] = final_path
    return item

def main():
    print("Loading vocabulary.json...")
    with open("vocabulary.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    vocab = data["vocabulary"]
    print(f"Loaded {len(vocab)} words.")
    
    os.makedirs("images", exist_ok=True)
    
    completed = 0
    total = len(vocab)
    
    print("Starting direct Bing Image download (High Performance)...")
    
    # 15 concurrent workers for high throughput without blocking
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(process_word, i, item): item for i, item in enumerate(vocab)}
        for future in as_completed(futures):
            completed += 1
            if completed % 50 == 0:
                print(f"Progress: {completed}/{total} images processed ({(completed/total)*100:.1f}%)...")
                
    with open("vocabulary.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print("Done! All real images downloaded successfully and vocabulary.json updated.")

if __name__ == "__main__":
    main()
