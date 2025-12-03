import os
import requests
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# Flask app for Render
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 PHONE OSINT BOT is running on Render!"

@app.route('/health')
def health():
    return "✅ Bot is healthy!", 200

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# Start Flask in background
Thread(target=run_flask, daemon=True).start()

# Bot Configuration - Render Environment Variables
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8133993773:AAG_pRTiU2M_X-nKdD31HrAe-dXeAHuMDKo")
ADMIN_ID = 8472134640

# OSINT API URL
OSINT_API = "https://osint-info.great-site.net/num.php?key=Vishal&phone="

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_phone_info(phone_number):
    """Fetch phone information from OSINT API"""
    try:
        response = requests.get(OSINT_API + phone_number, timeout=15)
        logger.info(f"API Status: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        logger.error(f"API Error: {e}")
        return None

def format_phone_info(data, phone):
    """Format phone information"""
    if not data or not data.get('success'):
        return "❌ *No information found for this number.*"
    
    results = data.get('results', [])
    if not results:
        return "❌ *No records found.*"
    
    text = f"""
📱 *PHONE OSINT LOOKUP*
➖➖➖➖➖➖➖➖➖➖
📞 *Number:* `{phone}`
📊 *Records:* {len(results)}
➖➖➖➖➖➖➖➖➖➖
"""
    
    for i, record in enumerate(results, 1):
        # Clean address
        address = record.get('address', 'N/A')
        if address:
            address = address.replace('!', ', ')
        
        text += f"""
📋 *Record #{i}*
👤 *Name:* {record.get('name', 'N/A')}
👨‍👩‍👦 *Father:* {record.get('father_name', 'N/A')}
📱 *Mobile:* `{record.get('mobile', 'N/A')}`
🏠 *Address:* {address}
📞 *Alternate:* `{record.get('alternate_mobile', 'N/A')}`
🌐 *Telecom:* {record.get('telecom_circle', 'N/A')}
🆔 *ID:* `{record.get('id_number', 'N/A')}`
➖➖➖➖➖➖➖➖➖➖
"""
    
    text += "\n⚡ *Hosted on Render* | 👤 *By @maarjauky*"
    return text

def get_ip_info(ip):
    """Get IP information"""
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# Telegram Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    keyboard = [
        [KeyboardButton("📱 Phone Lookup"), KeyboardButton("🌐 IP Lookup")],
        [KeyboardButton("📊 Status"), KeyboardButton("ℹ️ Help")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = f"""
🤖 *PHONE OSINT BOT* 

*Hello {user.first_name}!* I'm your phone lookup bot hosted on Render.

✅ *API STATUS: WORKING*
⚡ *HOST: RENDER (24/7)*

✨ *Features:*
• 📱 Phone Number OSINT Lookup
• 🌐 IP Address Information
• 🆓 Completely Free Service

📌 *Example:* Send `8799610678` for demo
    """
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    logger.info(f"Start command from {user.id}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📋 *BOT HELP GUIDE*

🤖 *How to Use:*
1. Tap 'Phone Lookup' button
2. Send 10-digit phone number
3. Get instant OSINT data

📱 *Phone Lookup Returns:*
• Owner Name & Father's Name
• Complete Address
• Alternate Phone Numbers
• Telecom Circle Details
• Identification Numbers

🌐 *IP Lookup:* Get geolocation info

⚡ *Hosted on Render - 24/7 Uptime*
👤 *Developer: @maarjauky*
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "📱 Phone Lookup":
        await update.message.reply_text("📱 *Phone Lookup*\n\nSend me a 10-digit phone number:\n\nExample: `8799610678`", parse_mode='Markdown')
        context.user_data['awaiting'] = 'phone'
        
    elif text == "🌐 IP Lookup":
        await update.message.reply_text("🌐 *IP Lookup*\n\nSend me an IP address:\n\nExample: `8.8.8.8`", parse_mode='Markdown')
        context.user_data['awaiting'] = 'ip'
        
    elif text == "📊 Status":
        await update.message.reply_text("✅ *BOT STATUS*\n\n🟢 **ONLINE**\n⚡ **Host:** Render\n📱 **API:** Working\n👤 **Users:** Unlimited\n🆓 **Free:** Forever", parse_mode='Markdown')
        
    elif text == "ℹ️ Help":
        await help_command(update, context)
        
    elif 'awaiting' in context.user_data:
        action = context.user_data['awaiting']
        
        if action == 'phone':
            if text.isdigit() and len(text) == 10:
                msg = await update.message.reply_text("🔍 *Searching database...*", parse_mode='Markdown')
                result = get_phone_info(text)
                
                if result:
                    response = format_phone_info(result, text)
                else:
                    response = "❌ *API temporarily unavailable.*\n\nPlease try again in 30 seconds."
                
                await update.message.reply_text(response, parse_mode='Markdown')
                await msg.delete()
            else:
                await update.message.reply_text("❌ *Invalid format!*\n\nSend exactly 10 digits.", parse_mode='Markdown')
                
        elif action == 'ip':
            if len(text.split('.')) == 4:
                msg = await update.message.reply_text("🔍 *Looking up IP...*", parse_mode='Markdown')
                result = get_ip_info(text)
                
                if result and result.get('status') == 'success':
                    response = f"""
🌐 *IP LOOKUP RESULTS*
➖➖➖➖➖➖➖➖➖➖
📍 *IP:* `{text}`
🏙️ *City:* {result.get('city', 'N/A')}
🏛️ *Region:* {result.get('regionName', 'N/A')}
🌍 *Country:* {result.get('country', 'N/A')}
📡 *ISP:* {result.get('isp', 'N/A')}
🕐 *Timezone:* {result.get('timezone', 'N/A')}
➖➖➖➖➖➖➖➖➖➖
                    """
                else:
                    response = "❌ *Could not fetch IP information*"
                
                await update.message.reply_text(response, parse_mode='Markdown')
                await msg.delete()
            else:
                await update.message.reply_text("❌ *Invalid IP!*\n\nExample: 8.8.8.8", parse_mode='Markdown')
        
        context.user_data.pop('awaiting', None)
        
    else:
        await update.message.reply_text("🤖 *Please select from menu!*", parse_mode='Markdown')

def main():
    """Start the bot - Render optimized"""
    logger.info("🚀 Starting bot on Render...")
    
    try:
        # Create application with webhook settings for Render
        application = Application.builder().token(BOT_TOKEN).build()

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        logger.info("✅ Bot initialized successfully!")
        logger.info("📱 OSINT API: Ready")
        logger.info("🌐 Render: Hosted")
        logger.info("🤖 Bot is running with polling...")
        
        # Use polling for Render (more stable than webhook)
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")

if __name__ == '__main__':
    main()