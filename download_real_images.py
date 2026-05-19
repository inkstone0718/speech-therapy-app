import os
import json
import io
import urllib.request
import urllib.parse
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed
from deep_translator import GoogleTranslator
from PIL import Image, ImageDraw, ImageFont

ssl._create_default_https_context = ssl._create_unverified_context

WIKI_API = "https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrsearch={}&gsrnamespace=6&gsrlimit=1&prop=imageinfo&iiprop=url"

# For Text Image Fallback
def create_text_image(text, output_path):
    # Create 200x200 green square
    img = Image.new('RGB', (200, 200), color='#4CAF50')
    draw = ImageDraw.Draw(img)
    
    # Try to load a Chinese font (Mac usually has PingFang or STHeiti)
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/Library/Fonts/Arial Unicode.ttf"
    ]
    font = None
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                # Load first font found
                font = ImageFont.truetype(fp, 50)
                break
            except:
                pass
    if font is None:
        font = ImageFont.load_default()
        
    # Center text
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(((200-w)/2, (200-h)/2), text, font=font, fill="white")
    
    img.save(output_path, "JPEG", quality=85)

def download_and_compress(url, output_path):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 SpeechTherapy/1.0'})
    response = urllib.request.urlopen(req, timeout=10)
    image_data = response.read()
    
    img = Image.open(io.BytesIO(image_data))
    # Convert to RGB (in case of PNG/RGBA)
    if img.mode in ('RGBA', 'P', 'CMYK'):
        img = img.convert('RGB')
        
    # Center crop to square
    width, height = img.size
    new_dim = min(width, height)
    left = (width - new_dim)/2
    top = (height - new_dim)/2
    right = (width + new_dim)/2
    bottom = (height + new_dim)/2
    
    img = img.crop((left, top, right, bottom))
    img = img.resize((200, 200), Image.Resampling.LANCZOS)
    img.save(output_path, "JPEG", quality=80)

def process_word(item):
    word = item["text"]
    # use encode to handle weird chars in path, but simple chinese works fine on mac
    output_path = f"images/{word}.jpg"
    
    # Skip if already downloaded
    if os.path.exists(output_path):
        item["imageUrl"] = output_path
        return item
        
    try:
        # Create a new translator for each thread to avoid concurrency issues
        translator = GoogleTranslator(source='zh-TW', target='en')
        en_word = translator.translate(word)
        
        # Search Wikimedia
        query = urllib.parse.quote(en_word)
        req = urllib.request.Request(WIKI_API.format(query), headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=10)
        data = json.loads(res.read())
        
        pages = data.get('query', {}).get('pages', {})
        if pages:
            page_id = list(pages.keys())[0]
            image_url = pages[page_id]['imageinfo'][0]['url']
            
            # Download and compress
            download_and_compress(image_url, output_path)
        else:
            # Fallback to Text Image
            create_text_image(word, output_path)
            
    except Exception as e:
        # Fallback
        try:
            create_text_image(word, output_path)
        except Exception:
            pass
            
    item["imageUrl"] = output_path
    return item

def main():
    print("Loading vocabulary.json...")
    with open("vocabulary.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    vocab = data["vocabulary"]
    print(f"Loaded {len(vocab)} words.")
    
    completed = 0
    total = len(vocab)
    
    print("Starting massive download process...")
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(process_word, item): item for item in vocab}
        for future in as_completed(futures):
            completed += 1
            if completed % 50 == 0:
                print(f"Processed {completed}/{total} images...")
                
    with open("vocabulary.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print("Done! All images saved to images/ and vocabulary.json updated.")

if __name__ == "__main__":
    main()
