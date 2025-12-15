import requests
import json

url = "http://localhost:8000/sweeper/preview"

payload = {
    "goal": "Test Preview",
    "queries": [
        {"q": "newer_than:7d", "max_results": 5}
    ],
    "actions": [
        {"type": "label", "name": "TestLabel"}
    ],
    "dry_run": True,
    "confirm": False,
    "limits": {
        "max_threads": 10,
        "allow_labels": ["TestLabel", "Newsletters", "Receipts", "Sandbox/Drafts"]
    }
}

try:
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    response.raise_for_status()
    data = response.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
