import json
import os

HISTORY_FILE = "paper_history.json"

def save_to_history(paper_data):
    """Save formatted paper to local history."""
    history = load_history()
    # Add timestamp as ID if not present
    import datetime
    if "timestamp" not in paper_data:
        paper_data["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    history.insert(0, paper_data)
    # Keep last 20
    history = history[:20]
    
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

def load_history():
    """Load paper history from local JSON."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def delete_from_history(index):
    """Delete a paper from history by index."""
    history = load_history()
    if 0 <= index < len(history):
        history.pop(index)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4)
        return True
    return False
