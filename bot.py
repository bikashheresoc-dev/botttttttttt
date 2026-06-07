import telebot
from telebot import types
import json
import os

# ==================== ⚙️ FIXED CONFIGURATION (Aapki Real Details) ====================
BOT_TOKEN = "8892483341:AAFiBOUDl8_tctBhfRwMp2SKc_u_ucSKLOs"
ADMIN_ID = 6132146801
CHANNEL_ID = "-1003729386499"
# ===================================================================================

CHANNEL_LINK = "https://t.me/nobitaosint"
BOT1_LINK = "https://t.me/nobita_infoo_bot"
BOT2_LINK = "https://t.me/upi_givewaybot"

# Professional UI Images
START_IMG = "https://images.unsplash.com/photo-1621416894569-0f39ed31d247?q=80&w=1000" 
REFER_IMG = "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?q=80&w=1000"

DB_FILE = "users_db.json"
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)
        return {}
    
    try:
        with open(DB_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except json.JSONDecodeError:
        with open(DB_FILE, "w") as f:
            json.dump({}, f)
        return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_user(user_id, username="User"):
    db = load_db()
    uid = str(user_id)
    if uid not in db:
        db[uid] = {
            "username": username,
            "balance": 0.0,
            "referred_by": None,
            "referrals_count": 0
        }
        save_db(db)
    return db[uid]

def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        if status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception:
        return False

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    username = message.from_user.username or f"User_{user_id}"
    
    args = message.text.split()
    referrer_id = None
    if len(args) > 1 and args[1].isdigit():
        referrer_id = int(args[1])

    user = get_user(user_id, username)

    if not is_subscribed(user_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK),
            types.InlineKeyboardButton("🤖 Start Bot 1", url=BOT1_LINK),
            types.InlineKeyboardButton("🤖 Start Bot 2", url=BOT2_LINK),
            types.InlineKeyboardButton("✅ Verified / Check", callback_data=f"check_sub_{referrer_id or 'none'}")
        )
        
        bot.send_photo(
            message.chat.id, 
            START_IMG,
            caption=f"👋 *Welcome {username} to Earning Easy Bot!*\n\n💰 Yahan aap har ek refer par *$1* kama sakte hain.\n\n⚠️ *Mandatory Step:* Bot use karne ke liye sabhi channels ko join aur bots ko start karke *✅ Verified / Check* par click karein!",
            reply_markup=markup
        )
        return

    show_main_menu(message.chat.id, user)

def show_main_menu(chat_id, user):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("👥 Refer & Earn", "💰 My Balance", "💳 Withdraw", "📊 Statistics")
    bot.send_message(
        chat_id, 
        f"🔥 *Main Menu*\n\nAapka account fully verified hai. Earning shuru karne ke liye niche buttons ka use karein.",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('check_sub_'))
def callback_check_sub(call):
    user_id = call.from_user.id
    username = call.from_user.username or f"User_{user_id}"
    referrer_id_str
