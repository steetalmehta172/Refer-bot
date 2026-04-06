import os
import sqlite3
import random
import time
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = os.getenv("8431814636:AAGzXIP40fckDGLc1lMVXwL0SwhxVJ2oxZ8")
ADMIN_ID = 7979064736  # apna Telegram ID daalo

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# DATABASE
conn = sqlite3.connect("bot.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
user_id INTEGER PRIMARY KEY,
balance INTEGER DEFAULT 0,
total INTEGER DEFAULT 0,
referred_by INTEGER,
ref_count INTEGER DEFAULT 0,
last_bonus INTEGER DEFAULT 0
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS withdraw(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
amount INTEGER,
method TEXT,
status TEXT DEFAULT 'pending'
)
""")

conn.commit()

# MENU
menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
menu.add("💰 Watch Ads","💳 Balance")
menu.add("🎁 Bonus","👥 Refer")
menu.add("📋 Tasks","💸 Withdraw")

# START + REFERRAL
@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    user_id = msg.from_user.id
    args = msg.get_args()

    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cur.fetchone()

    if not user:
        ref = int(args) if args.isdigit() else None
        cur.execute("INSERT INTO users (user_id,referred_by) VALUES (?,?)",(user_id,ref))
        conn.commit()

    await msg.answer("🔥 Welcome to Earn Bot 💰", reply_markup=menu)

# BALANCE
@dp.message_handler(lambda m: m.text=="💳 Balance")
async def balance(msg: types.Message):
    cur.execute("SELECT balance,total,ref_count FROM users WHERE user_id=?",(msg.from_user.id,))
    b,t,r = cur.fetchone()
    await msg.answer(f"💰 Balance: ₹{b}\n📈 Total: ₹{t}\n👥 Referrals: {r}")

# ADS
@dp.message_handler(lambda m: m.text=="💰 Watch Ads")
async def ads(msg: types.Message):
    await msg.answer("🔗 Open Ad:\nhttps://yourdomain.com/ads.html\nWait 10 sec then click Done")

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("✅ Done")
    await msg.answer("After watching click below", reply_markup=kb)

# DONE ADS
@dp.message_handler(lambda m: m.text=="✅ Done")
async def done(msg: types.Message):
    user_id = msg.from_user.id
    reward = random.randint(3,5)

    cur.execute("UPDATE users SET balance=balance+?, total=total+? WHERE user_id=?",(reward,reward,user_id))
    conn.commit()

    # REF COMMISSION
    cur.execute("SELECT referred_by FROM users WHERE user_id=?",(user_id,))
    ref = cur.fetchone()[0]

    if ref:
        bonus = int(reward*0.05)
        cur.execute("UPDATE users SET balance=balance+? WHERE user_id=?",(bonus,ref))
        conn.commit()

    await msg.answer(f"✅ Earned ₹{reward}", reply_markup=menu)

# BONUS
@dp.message_handler(lambda m: m.text=="🎁 Bonus")
async def bonus(msg: types.Message):
    user_id = msg.from_user.id
    now = int(time.time())

    cur.execute("SELECT last_bonus FROM users WHERE user_id=?",(user_id,))
    last = cur.fetchone()[0]

    if now-last >= 86400:
        cur.execute("UPDATE users SET balance=balance+5,last_bonus=? WHERE user_id=?",(now,user_id))
        conn.commit()
        await msg.answer("🎉 ₹5 Bonus Added")
    else:
        await msg.answer("⏳ Already claimed")

# REFERRAL
@dp.message_handler(lambda m: m.text=="👥 Refer")
async def refer(msg: types.Message):
    link = f"https://t.me/Refertoearn98_bot?start={msg.from_user.id}"
    await msg.answer(f"Invite & Earn ₹40\n\n🔗 {link}")

# TASKS
@dp.message_handler(lambda m: m.text=="📋 Tasks")
async def tasks(msg: types.Message):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("📺 Subscribe", url="https://www.youtube.com/@Tollfacecome"))
    kb.add(types.InlineKeyboardButton("📢 Join Telegram", url="https://t.me/codestore90"))
    kb.add(types.InlineKeyboardButton("✅ Done Tasks", callback_data="done"))

    await msg.answer("Complete tasks to earn ₹20", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data=="done")
async def done_task(call: types.CallbackQuery):
    user_id = call.from_user.id

    cur.execute("UPDATE users SET balance=balance+20 WHERE user_id=?",(user_id,))
    conn.commit()

    await call.message.answer("✅ Task completed ₹20 added")

# WITHDRAW
@dp.message_handler(lambda m: m.text=="💸 Withdraw")
async def withdraw(msg: types.Message):
    await msg.answer("Send amount + UPI\nExample: 100 upi@paytm")

@dp.message_handler(lambda m: m.text and m.text.split()[0].isdigit())
async def process_withdraw(msg: types.Message):
    user_id = msg.from_user.id
    amount, method = msg.text.split(maxsplit=1)

    cur.execute("INSERT INTO withdraw (user_id,amount,method) VALUES (?,?,?)",(user_id,amount,method))
    conn.commit()

    await msg.answer("✅ Withdraw request sent")

    await bot.send_message(ADMIN_ID,f"💸 Withdraw Request\nUser: {user_id}\nAmount: ₹{amount}\nMethod: {method}")

# ADMIN COMMAND
@dp.message_handler(commands=['admin'])
async def admin(msg: types.Message):
    if msg.from_user.id == ADMIN_ID:
        await msg.answer("👑 Admin Panel Active")

if __name__ == "__main__":
    executor.start_polling(dp)
