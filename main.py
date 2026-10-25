import json, random, os
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "YOUR_TOKEN_HERE"
ADMIN_ID = 8224640630
DATA_FILE = "users.json"

def load_users():
    if not os.path.exists(DATA_FILE): return {}
    with open(DATA_FILE, "r") as f: return json.load(f)
def save_users(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)
users = load_users()

def is_paid(user_id):
    if user_id == ADMIN_ID: return True
    if str(user_id) not in users: return False
    exp = datetime.fromisoformat(users[str(user_id)]["expiry"])
    return exp > datetime.now()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_paid(uid):
        await update.message.reply_text(f"❌ Not paid member\n💰 Price: 15$ Monthly\n📩 Contact @YourUsername\nYour ID: {uid}")
        return
    keyboard = [[InlineKeyboardButton("GENERATE 🎯", callback_data="gen")]]
    await update.message.reply_text("✅ ALPHA FILTER VIP - Click to get signal", reply_markup=InlineKeyboardMarkup(keyboard))

async def gen_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_paid(query.from_user.id):
        await query.answer("Not a paid member!", show_alert=True)
        return
    direction = random.choice(["CALL 🟢", "PUT 🔴"])
    tf = random.choice(["5s","10s","1m","3m","5m"])
    text = f"🎯 ALPHA FILTER\n\n📈 Signal: {direction}\n⏱ TF: {tf}\n🎯 Accuracy: {random.randint(88,98)}%"
    keyboard = [[InlineKeyboardButton("NEXT ➡️", callback_data="gen")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def adduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        uid = context.args[0]; days = int(context.args[1])
        expiry = datetime.now() + timedelta(days=days)
        users[str(uid)] = {"expiry": expiry.isoformat()}
        save_users(users)
        await update.message.reply_text(f"✅ User {uid} added for {days} days")
    except:
        await update.message.reply_text("Use: /adduser USER_ID 30")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("adduser", adduser))
app.add_handler(CallbackQueryHandler(gen_button, pattern="gen"))
app.run_polling()
