import telebot
from telebot import types
import json
import os

# ==================== ⚙️ CONFIGURATION ====================
BOT_TOKEN = "8787151484:AAGmdAlrtBa61IUJ7OW8CuCIsbYlOjVR55c"
ADMIN_ID = 6132146801
CHANNEL_ID = "-1003729386499"
# ==========================================================

CHANNEL_LINK = "https://t.me/nobitaosint"
BOT1_LINK = "https://t.me/nobita_infoo_bot"
BOT2_LINK = "https://t.me/upi_givewaybot"

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
                # Agar file khali hai toh empty dict return karo
                return {}
            return json.loads(content)
    except json.JSONDecodeError:
        # JSONDecodeError aane par file ko auto-fix/reset karo taaki bot crash na ho
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
    referrer_id_str = call.data.split('_')[2]
    
    if is_subscribed(user_id):
        db = load_db()
        uid = str(user_id)
        
        if uid not in db:
            db[uid] = {
                "username": username,
                "balance": 0.0,
                "referred_by": None,
                "referrals_count": 0
            }
            if referrer_id_str != 'none' and referrer_id_str != uid:
                if referrer_id_str in db:
                    db[referrer_id_str]["balance"] += 1.0
                    db[referrer_id_str]["referrals_count"] += 1
                    db[uid]["referred_by"] = referrer_id_str
                    try:
                        bot.send_message(int(referrer_id_str), f"🎉 *New Referral!* @{username} aapke link se join hua. Aapko *$1* mil gaye hain!")
                    except:
                        pass
            save_db(db)
        
        bot.answer_callback_query(call.id, "✅ Verification Successful!")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        show_main_menu(call.message.chat.id, db[uid])
    else:
        bot.answer_callback_query(call.id, "❌ Aapne abhi tak saare tasks poore nahi kiye hain!", show_alert=True)

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    user_id = message.from_user.id
    db = load_db()
    uid = str(user_id)
    
    if uid not in db or not is_subscribed(user_id):
        bot.send_message(message.chat.id, "⚠️ Pehle `/start` karke mandatory channels join karein.")
        return

    user = db[uid]

    if message.text == "👥 Refer & Earn":
        bot_username = bot.get_me().username
        ref_link = f"https://t.me/{bot_username}?start={user_id}"
        bot.send_photo(
            message.chat.id,
            REFER_IMG,
            caption=f"👥 *Referral Program*\n\n🔗 *Aapka Unique Link:*\n`{ref_link}`\n\n💵 *Per Refer:* $1\n🎯 Har valid join par aapko instantly $1 milega."
        )

    elif message.text == "💰 My Balance":
        bot.send_message(
            message.chat.id,
            f"💳 *Aapka Wallet Balance*\n\n💰 Balance: *${user['balance']:.2f}*\n👥 Total Refers: `{user['referrals_count']}`"
        )

    elif message.text == "💳 Withdraw":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🌐 Binance ($5 Min)", callback_data="wd_crypto"),
            types.InlineKeyboardButton("🇮🇳 UPI ($7 Min)", callback_data="wd_upi")
        )
        bot.send_message(message.chat.id, "💵 *Withdrawal Portal*\n\nSelect method:", reply_markup=markup)

    elif message.text == "📊 Statistics":
        total_users = len(db)
        bot.send_message(message.chat.id, f"📊 *Live Bot Stats*\n\n👥 Total Users: `{total_users}`\n⚡ Powered by @earningeasy_freebot")

@bot.callback_query_handler(func=lambda call: call.data.startswith('wd_'))
def process_withdrawal(call):
    user_id = call.from_user.id
    db = load_db()
    user = db[str(user_id)]
    method = call.data.split('_')[1]

    if method == "crypto":
        if user['balance'] < 5.0:
            bot.answer_callback_query(call.id, "❌ Minimum withdrawal Crypto ke liye $5 hai!", show_alert=True)
            return
        msg = bot.send_message(call.message.chat.id, "📝 Apna *Binance Pay ID* ya *USDT Address* bhejein:")
        bot.register_next_step_handler(msg, save_crypto_request, user['balance'])

    elif method == "upi":
        if user['balance'] < 7.0:
            bot.answer_callback_query(call.id, "❌ Minimum withdrawal UPI ke liye $7 hai!", show_alert=True)
            return
        msg = bot.send_message(call.message.chat.id, "📝 Apna valid *UPI ID* bhejein:")
        bot.register_next_step_handler(msg, save_upi_request, user['balance'])

def save_crypto_request(message, amount):
    address = message.text
    user_id = message.from_user.id
    db = load_db()
    uid = str(user_id)
    
    if db[uid]['balance'] >= amount:
        db[uid]['balance'] = 0.0
        save_db(db)
        bot.send_message(ADMIN_ID, f"🔔 *NEW WITHDRAW REQUEST (Crypto)*\n\n👤 User ID: `{user_id}`\n💰 Amount: ${amount}\n🏠 Address: `{address}`")
        bot.send_message(message.chat.id, "✅ Payout Request submit ho gayi hai!")

def save_upi_request(message, amount):
    upi_id = message.text
    user_id = message.from_user.id
    db = load_db()
    uid = str(user_id)
    
    if db[uid]['balance'] >= amount:
        db[uid]['balance'] = 0.0
        save_db(db)
        bot.send_message(ADMIN_ID, f"🔔 *NEW WITHDRAW REQUEST (UPI)*\n\n👤 User ID: `{user_id}`\n💰 Amount: ${amount}\n🇮🇳 UPI: `{upi_id}`")
        bot.send_message(message.chat.id, "✅ UPI Payout Request submit ho gayi hai!")

bot.infinity_polling()
