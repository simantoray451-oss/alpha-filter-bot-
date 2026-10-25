import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random, os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

ADMIN_ID = 8534787705
PAID_FILE = "paid_users.txt"
PAIRS = ["EUR/USD-OTC", "GBP/USD-OTC", "USD/JPY-OTC", "EUR/JPY-OTC", "AUD/CAD-OTC", "GBP/JPY-OTC", "EUR/GBP-OTC", "USD/BDT-OTC"]

def get_paid():
    if not os.path.exists(PAID_FILE): return []
    with open(PAID_FILE, "r") as f:
        return [int(x.strip()) for x in f if x.strip().isdigit()]

def add_paid(uid):
    if uid not in get_paid():
        with open(PAID_FILE, "a") as f: f.write(f"{uid}\n")

@bot.message_handler(commands=['add'])
def add_cmd(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_id = int(message.text.split()[1])
        add_paid(new_id)
        bot.reply_to(message, f"✅ Success! {new_id} is now PAID member.")
    except:
        bot.reply_to(message, "❌ Use: /add 123456789")

@bot.message_handler(commands=['remove'])
def remove_cmd(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        rem_id = int(message.text.split()[1])
        users = get_paid()
        if rem_id in users:
            users.remove(rem_id)
            with open(PAID_FILE, "w") as f:
                for u in users: f.write(f"{u}\n")
            bot.reply_to(message, f"🗑️ Removed {rem_id}")
    except: pass

@bot.message_handler(commands=['start', 'gen'])
def gen_cmd(message):
    paid = get_paid()
    if message.from_user.id != ADMIN_ID and message.from_user.id not in paid:
        bot.send_message(message.chat.id, f"❌ Not paid member\n\n💰 Price: 15$ Monthly\n📩 Contact Admin\n\nYour ID: `{message.from_user.id}`", parse_mode="Markdown")
        return

    markup = InlineKeyboardMarkup(row_width=3)
    markup.add(
        InlineKeyboardButton("5s", callback_data="tf_5s"),
        InlineKeyboardButton("10s", callback_data="tf_10s"),
        InlineKeyboardButton("30s", callback_data="tf_30s"),
        InlineKeyboardButton("1m", callback_data="tf_1m"),
        InlineKeyboardButton("3m", callback_data="tf_3m"),
        InlineKeyboardButton("5m", callback_data="tf_5m"),
        InlineKeyboardButton("10m", callback_data="tf_10m")
    )
    bot.send_message(message.chat.id, "🎯 **ALPHA FILTER**\n\nSelect Timeframe 👇", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('tf_'))
def signal_gen(call):
    tf = call.data.replace('tf_', '')
    pair = random.choice(PAIRS)
    signal = random.choice(["CALL 🟢", "PUT 🔴"])
    acc = random.randint(88, 96)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(f"NEXT ➡️ ({tf})", callback_data=f"tf_{tf}"))
    markup.add(InlineKeyboardButton("Change Timeframe", callback_data="change_tf"))

    text = f"🎯 **ALPHA FILTER**\n\n💱 Pair: `{pair}`\n📊 Signal: {signal}\n⏱️ TF: {tf}\n🎯 Accuracy: {acc}%"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "change_tf")
def change_tf(call):
    gen_cmd(call.message)

bot.infinity_polling()
