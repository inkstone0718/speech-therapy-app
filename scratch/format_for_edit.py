import json

def main():
    try:
        with open("preview_vocab.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("preview_vocab.json not found. Please run generate_concrete_vocab.py first.")
        return
        
    flat_vocab = data["vocabulary"]
    
    # Structure it: key is "INITIAL_SYLLABLES_POSITION" (1-indexed position)
    structured = {}
    for item in flat_vocab:
        key = f"{item['initial']}_{item['syllables']}_{item['targetIndex'] + 1}"
        if key not in structured:
            structured[key] = []
        if item["text"] not in structured[key]:
            structured[key].append(item["text"])
            
    # Ensure they all have exactly 20 items (if duplicates were removed, pad them or just keep unique)
    # Actually, the user might want to see the unique list, but let's keep all 20 so they can edit each card individually.
    # So we should not use "not in structured[key]" if we want exactly 20 slots.
    # Let's keep exactly 20 slots.
    structured = {}
    for item in flat_vocab:
        key = f"{item['initial']}_{item['syllables']}_{item['targetIndex'] + 1}"
        if key not in structured:
            structured[key] = []
        structured[key].append(item["text"])
        
    with open("vocabulary_edit.json", "w", encoding="utf-8") as f:
        json.dump(structured, f, ensure_ascii=False, indent=2)
        
    print("Exported to vocabulary_edit.json! You can now view and edit the words in this file.")

if __name__ == "__main__":
    main()
