import json

FIREBASE_DOMAIN = "https://speech-therapy-174df.web.app"

def main():
    try:
        with open("vocabulary.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("vocabulary.json not found.")
        return
        
    vocab = data["vocabulary"]
    updated_count = 0
    
    for item in vocab:
        img_url = item.get("imageUrl", "")
        if img_url.startswith("images/"):
            # Convert to absolute URL
            item["imageUrl"] = f"{FIREBASE_DOMAIN}/{img_url}"
            updated_count += 1
            
    if updated_count > 0:
        with open("vocabulary.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Successfully converted {updated_count} local paths to absolute Firebase Hosting CDN URLs!")
        print("You can now safely delete the local 'images/' directory to free up your computer's storage space!")
    else:
        print("No local image paths found to convert.")

if __name__ == "__main__":
    main()
