"""
Test script to send 100 notes to the /add-note endpoint
Run this after starting the FastAPI server
"""

import requests
import time
from test_data import test_notes

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust if your server runs on different port
API_ENDPOINT = f"{BASE_URL}/api/v1/note/add-note"

def send_note(text: str, index: int):
    """Send a single note to the API"""
    try:
        response = requests.post(
            API_ENDPOINT,
            params={"text": text},
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ [{index + 1}/100] Success - Created {result.get('items_created', 0)} items")
            return True
        else:
            print(f"❌ [{index + 1}/100] Failed - Status {response.status_code}: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ [{index + 1}/100] Error: {e}")
        return False

def main():
    print(f"🚀 Starting test ingestion of {len(test_notes)} notes...")
    print(f"📍 Target endpoint: {API_ENDPOINT}\n")

    success_count = 0
    failed_count = 0

    start_time = time.time()

    for i, note in enumerate(test_notes):
        print(f"📝 Sending: {note[:50]}...")

        if send_note(note, i):
            success_count += 1
        else:
            failed_count += 1

        # Small delay to avoid overwhelming the API
        time.sleep(0.5)

    end_time = time.time()
    duration = end_time - start_time

    print("\n" + "="*60)
    print("📊 Test Results:")
    print(f"   ✅ Successful: {success_count}/{len(test_notes)}")
    print(f"   ❌ Failed: {failed_count}/{len(test_notes)}")
    print(f"   ⏱️  Duration: {duration:.2f} seconds")
    print(f"   📈 Average: {duration/len(test_notes):.2f}s per note")
    print("="*60)

if __name__ == "__main__":
    print("\n🔍 Pre-flight check...")

    # Check if server is running
    try:
        health_check = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_check.status_code == 200:
            print("✅ Server is running\n")
            main()
        else:
            print("❌ Server returned unexpected status")
    except requests.exceptions.RequestException:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print("   Make sure FastAPI server is running:")
        print("   $ uvicorn main:app --reload")
