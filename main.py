import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random, os, json
from datetime import datetime, timedelta

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

ADMIN_ID = 8534787705
PAID_FILE = "paid_users.txt"
STATS_FILE = "stats.json"
PAIRS = ["EUR/USD-OTC", "GBP/USD-OTC", "USD/JPY-OTC", "EUR/GBP-OTC", "USD/BDT-OTC"]
BROKERS = ["Quotex", "Binomo", "Pocket Option", "IQ Option"]

def get_paid():
    if not os.path.exists(PAID_FILE): return []
    with open(PAID_FILE, "r") as f:
        return [int(x.strip()) for x in f if x.strip().isdigit()]

def add_paid(uid):
    if uid not in get_paid():
        with open(PAID_FILE, "a") as f: f.write(f"{uid}\n")

def get_stats():
    if not os.path.exists(STATS_FILE): return {"win":0, "loss":0}
    try:
        with open(STATS_FILE, "r") as f: return json.load(f)
    except: return {"win":0, "loss":0}

def save_stats(win, loss):
    s = get_stats()
    s["win"] += win
    s["loss"] += loss
    with open(STATS_FILE, "w") as f: json.dump(s, f)

@bot.message_handler(commands=['start'])
def start(m):
    if m.from_user.id not in get_paid() and m.from_user.id != ADMIN_ID:
        bot.reply_to(m, f"❌ Paid member na.\nApnar ID: {m.from_user.id}\nAdmin ke ID ta din.")
        return
    bot.reply_to(m, "✅ Alpha Filter Bot Ready!\nUse /gen for demo signal")

@bot.message_handler(commands=['add'])
def add_cmd(m):
    if m.from_user.id != ADMIN_ID: return
    try:
        nid = int(m.text.split()[1])
        add_paid(nid)
        bot.reply_to(m, f"✅ Added {nid}")
    except: bot.reply_to(m, "Use: /add 123456")

@bot.message_handler(commands=['gen'])
def gen(m):
    if m.from_user.id not in get_paid() and m.from_user.id != ADMIN_ID: return
    mk = InlineKeyboardMarkup(row_width=2)
    for b in BROKERS:
        mk.add(InlineKeyboardButton(b, callback_data=f"bro_{b}"))
    bot.send_message(m.chat.id, "🏦 Select Broker:", reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data.startswith('bro_'))
def bro_sel(call):
    broker = call.data.split('_',1)[1]
    mk = InlineKeyboardMarkup(row_width=3)
    mk.add(InlineKeyboardButton("1M", callback_data=f"tf_1M_{broker}"),
           InlineKeyboardButton("2M", callback_data=f"tf_2M_{broker}"),
           InlineKeyboardButton("5M", callback_data=f"tf_5M_{broker}"))
    mk.add(InlineKeyboardButton("Change Broker", callback_data="change"))
    bot.edit_message_text(f"Broker: {broker}\nSelect Timeframe:", call.message.chat.id, call.message.message_id, reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data.startswith('tf_'))
def signal_gen(call):
    _, tf, broker = call.data.split('_', 2)
    pair = random.choice(PAIRS)
    direction = random.choice(["CALL 🟢 UP", "PUT 🔴 DOWN"])
    now = datetime.now()
    entry = (now + timedelta(minutes=1)).strftime("%H:%M:%S")
    
    s = get_stats()
    total = s["win"] + s["loss"]
    if total > 0:
        acc_text = f"{round(s['win']/total*100,2)}% based on {total} tracked results"
    else:
        acc_text = "No tracked results yet"

    mk = InlineKeyboardMarkup(row_width=2)
    mk.add(InlineKeyboardButton("✅ WIN", callback_data="res_win"), InlineKeyboardButton("❌ LOSS", callback_data="res_loss"))
    mk.add(InlineKeyboardButton(f"NEXT {tf}", callback_data=f"tf_{tf}_{broker}"), InlineKeyboardButton("Change", callback_data="change"))

    text = f"""⚠️ SIMULATED / DEMO - FOR EDUCATION ONLY
NOT FINANCIAL ADVICE

Broker: {broker}
Pair: {pair}
Direction: {direction}
Timeframe: {tf}
Entry: {entry}

Tracked Performance: {acc_text}
This signal is randomly generated for demo/testing of the bot interface. Do not use for real trading.
"""
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data.startswith('res_'))
def res_save(call):
    if call.data == "res_win": save_stats(1,0)
    else: save_stats(0,1)
    bot.answer_callback_query(call.id, "Saved! Use /gen for next demo")

@bot.callback_query_handler(func=lambda c: c.data == "change")
def change(call):
    gen(call.message)

bot.infinity_polling()
