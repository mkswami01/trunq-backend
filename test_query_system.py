"""
Test script to query the /chat endpoint with various questions
Run this after ingesting the 100 test notes
"""

import requests
import time
from test_queries import test_queries

# Configuration
BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{BASE_URL}/api/v1/note/chat"

def test_query(query: str, category: str):
    """Send a query to the chat endpoint"""
    try:
        response = requests.post(
            CHAT_ENDPOINT,
            params={"q": query},
            timeout=60
        )

        if response.status_code == 200:
            result = response.text if response.text else response.json()
            return True, result
        else:
            return False, f"Status {response.status_code}: {response.text}"

    except requests.exceptions.RequestException as e:
        return False, f"Error: {e}"

def main():
    print("🔍 Testing Query System\n")
    print("=" * 80)

    # Ask user which category to test
    print("\nAvailable categories:")
    for i, category in enumerate(test_queries.keys(), 1):
        print(f"  {i}. {category} ({len(test_queries[category])} queries)")

    print(f"  {len(test_queries) + 1}. All queries")

    choice = input(f"\nSelect category (1-{len(test_queries) + 1}): ").strip()

    if choice == str(len(test_queries) + 1):
        # Test all
        queries_to_test = []
        for category, queries in test_queries.items():
            for query in queries:
                queries_to_test.append((category, query))
    else:
        # Test specific category
        try:
            category_name = list(test_queries.keys())[int(choice) - 1]
            queries_to_test = [(category_name, q) for q in test_queries[category_name]]
        except (ValueError, IndexError):
            print("❌ Invalid choice")
            return

    print(f"\n🚀 Testing {len(queries_to_test)} queries...\n")
    print("=" * 80)

    for category, query in queries_to_test:
        print(f"\n📝 Category: {category}")
        print(f"❓ Query: \"{query}\"")
        print("-" * 80)

        success, result = test_query(query, category)

        if success:
            print(f"✅ Response:\n{result}\n")
        else:
            print(f"❌ Failed: {result}\n")

        print("=" * 80)

        # Pause between queries
        time.sleep(1)

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
