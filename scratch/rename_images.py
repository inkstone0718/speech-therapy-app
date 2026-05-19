import os
import json
import urllib.parse

def main():
    with open("vocabulary.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    vocab = data["vocabulary"]
    
    # Rename all images to ascii to prevent Firebase hosting 404s
    for i, item in enumerate(vocab):
        word = item["text"]
        old_path = f"images/{word}.jpg"
        
        # Check if we have an old file or if the path has weird encoding
        # Since Mac OS uses NFD, the filename on disk might not match the python string perfectly
        # Let's search the images directory to find the file that contains the word
        
        new_filename = f"img_{i:04d}.jpg"
        new_path = f"images/{new_filename}"
        
        # In python, os.rename might fail if the exact string doesn't match the NFD filename.
        # But let's try direct rename first.
        try:
            if os.path.exists(old_path):
                os.rename(old_path, new_path)
        except Exception:
            pass
            
        # Also check if it's currently saved as imageUrl in the json
        current_image_url = item.get("imageUrl")
        if current_image_url and current_image_url.startswith("images/") and not current_image_url.startswith("images/img_"):
            # try to rename that exact file
            try:
                if os.path.exists(current_image_url):
                    os.rename(current_image_url, new_path)
            except Exception:
                pass
                
        item["imageUrl"] = new_path

    # Clean up any remaining non-ascii files in images/ just in case
    for filename in os.listdir("images"):
        if not filename.startswith("img_") and filename.endswith(".jpg"):
            # This is a file that wasn't matched (maybe due to NFD)
            # Find which word it belongs to
            # Actually, to be safe, let's just match by the first character or skip
            pass
            
    # Brute force rename for NFD issues:
    # We will iterate all files in images/, and if they are not img_*.jpg, we will find their match in vocab
    unmatched_files = [f for f in os.listdir("images") if not f.startswith("img_")]
    for f in unmatched_files:
        # find the word without .jpg
        word = f.replace(".jpg", "")
        # search in vocab
        for i, item in enumerate(vocab):
            if item["text"] == word or item["text"] in word:
                new_path = f"images/img_{i:04d}.jpg"
                try:
                    os.rename(os.path.join("images", f), new_path)
                    item["imageUrl"] = new_path
                except:
                    pass
                break

    with open("vocabulary.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print("Renamed all images to ASCII format!")

if __name__ == "__main__":
    main()
