#!/usr/bin/env python3
"""
Test webhook server locally by simulating a button press
"""
import requests
import json

def test_webhook_locally():
    """Send a test webhook payload to our local server"""
    webhook_url = "https://127.0.0.1:8080/webhook"
    
    # Simulate a button press callback
    test_payload = {
        "update_id": 12345,
        "callback_query": {
            "id": "test123",
            "from": {
                "id": 7507609139,
                "username": "testuser"
            },
            "message": {
                "message_id": 123,
                "chat": {
                    "id": 7507609139
                },
                "text": "Original test message"
            },
            "data": "approve_LOCALTEST001"
        }
    }
    
    print("🧪 Testing webhook server locally...")
    print(f"Sending test payload to: {webhook_url}")
    
    try:
        response = requests.post(
            webhook_url,
            json=test_payload,
            verify=False,  # Skip SSL verification for self-signed cert
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.ok:
            print("✅ Webhook server responded successfully!")
        else:
            print("❌ Webhook server error")
            
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")

if __name__ == "__main__":
    test_webhook_locally()
