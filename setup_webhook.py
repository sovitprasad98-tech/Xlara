import requests

BOT_TOKEN = "8994349885:AAHHDvskvoL6-pdYxJmmq9UsI-FWTN-zYMU"
VERCEL_URL = "https://xlara-by-sx.vercel.app"  # 🔥 REPLACE YOUR VERCEL URL

def setup_webhook():
    webhook_url = f"{VERCEL_URL}/api/webhook"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    payload = {
        'url': webhook_url,
        'max_connections': 100,
        'allowed_updates': ['message', 'callback_query']
    }
    response = requests.post(url, json=payload)
    print(f"Webhook setup: {response.json()}")

def get_webhook_info():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
    response = requests.get(url)
    print(f"Webhook info: {response.json()}")

if __name__ == "__main__":
    print("🚀 Setting up webhook...")
    setup_webhook()
    print("\n📋 Checking webhook...")
    get_webhook_info()
