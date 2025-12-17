"""
Discord Webhook Test
Tests if your Discord webhook is valid and working
"""

import requests
import json

# Import your config
try:
    import config
except ImportError:
    print("ERROR: config.py not found!")
    exit(1)

print("=" * 50)
print("Discord Webhook Test")
print("=" * 50)
print(f"\nWebhook URL: {config.DISCORD_WEBHOOK_URL[:50]}...")
print("\n" + "=" * 50)

# Test 1: Simple text message
print("\n🔄 Test 1: Sending simple text message...")
try:
    payload = {
        "content": "✅ Test message from FS25 Mod Monitor - webhook is working!"
    }
    
    response = requests.post(config.DISCORD_WEBHOOK_URL, json=payload)
    
    if response.status_code == 204:
        print("✅ Simple message sent successfully!")
    else:
        print(f"❌ Failed with status code: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Simple embed (like the monitor uses)
print("\n🔄 Test 2: Sending embed message (like mod monitor)...")
try:
    payload = {
        "embeds": [{
            "title": "🚜 Test Embed - FS25 Mod Monitor",
            "color": 0x00FF00,
            "fields": [
                {
                    "name": "✅ Test Field",
                    "value": "**Title:** Test Mod\n**Version:** 1.0.0\n**Author:** Test Author\n**Size:** 10.00 MB",
                    "inline": False
                }
            ],
            "footer": {
                "text": "Test timestamp"
            }
        }]
    }
    
    response = requests.post(config.DISCORD_WEBHOOK_URL, json=payload)
    
    if response.status_code == 204:
        print("✅ Embed sent successfully!")
        print("\n" + "=" * 50)
        print("✅ WEBHOOK IS WORKING CORRECTLY!")
        print("=" * 50)
    else:
        print(f"❌ Failed with status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            print("\n🔍 400 Error Troubleshooting:")
            print("  1. Check webhook URL is complete (should be very long)")
            print("  2. Webhook might have been deleted in Discord")
            print("  3. Webhook might be for wrong server/channel")
            print("\n💡 Try creating a new webhook in Discord:")
            print("  - Right-click channel → Edit Channel")
            print("  - Integrations → Webhooks → New Webhook")
            print("  - Copy the URL and update config.py")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n✨ Test complete!")
