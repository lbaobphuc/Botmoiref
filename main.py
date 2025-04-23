from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from keep_alive import keep_alive
import asyncio
import os

TOKEN = "7726374817:AAFMgUVBQ0ABJiR0Wldoe1yoO4xcJkKRjro"
ADMIN_ID = 7865938276
REQUIRED_CHANNELS = ["@kiemvaidongle", "@kiemvaidonglechoae"]
REF_REWARD = 800
MIN_WITHDRAW = 8000
WEBHOOK_URL = "https://botmoiref.onrender.com"

users = {}
ip_ban_list = []

def menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Tài khoản", callback_data="account")],
        [InlineKeyboardButton("📤 Mời bạn bè", callback_data="ref")],
        [InlineKeyboardButton("📊 Thống kê", callback_data="stats")],
        [InlineKeyboardButton("💸 Rút tiền", callback_data="withdraw")]
    ])

async def is_user_in_channel(bot, user_id, channel):
    try:
        member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    ip = update.effective_user.username or "unknown"

    if ip in ip_ban_list:
        await update.message.reply_text("Bạn bị cấm sử dụng bot.")
        return

    if user_id not in users:
        users[user_id] = {"balance": 0, "invited": [], "ip": ip}
        if context.args:
            ref_id = context.args[0]
            if ref_id != user_id:
                if ref_id not in users:
                    users[ref_id] = {"balance": REF_REWARD, "invited": [user_id], "ip": "unknown"}
                else:
                    if user_id not in users[ref_id]["invited"]:
                        users[ref_id]["balance"] += REF_REWARD
                        users[ref_id]["invited"].append(user_id)
                await context.bot.send_message(chat_id=ref_id, text=f"🎉 Bạn vừa nhận {REF_REWARD}đ vì mời được 1 người!")
    else:
        if users[user_id]["ip"] != ip:
            for uid, data in users.items():
                if data["ip"] == ip and uid != user_id:
                    ip_ban_list.append(ip)
                    await update.message.reply_text("IP của bạn trùng với người khác. Bạn bị cấm sử dụng bot.")
                    return

    all_joined = True
    for channel in REQUIRED_CHANNELS:
        if not await is_user_in_channel(context.bot, user.id, channel):
            all_joined = False
            break

    if all_joined:
        await update.message.reply_text("✅ Bạn đã tham gia đủ kênh. Chọn chức năng bên dưới:", reply_markup=menu_keyboard())
    else:
        channel_list = "\n".join([f"➡️ {ch}" for ch in REQUIRED_CHANNELS])
        await update.message.reply_text(f"❗ Bạn cần tham gia các kênh sau để sử dụng bot:\n{channel_list}\n\nSau khi tham gia, vui lòng bấm /start lại.")

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)

    if user_id not in users:
        await query.edit_message_text("Bạn chưa bắt đầu bot. Gõ /start.")
        return

    if query.data == "account":
        balance = users[user_id]["balance"]
        text = f"💰 Số dư của bạn: {balance}đ"
    elif query.data == "ref":
        text = f"📮 Link mời bạn: https://t.me/Botkiemvaidongle_bot?start={user_id}"
    elif query.data == "stats":
        text = f"📊 Số người đã dùng bot: {len(users)}"
    elif query.data == "withdraw":
        balance = users[user_id]["balance"]
        if balance >= MIN_WITHDRAW:
            users[user_id]["balance"] = 0
            text = f"✅ Yêu cầu rút {balance}đ đã được gửi đến admin."
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"💸 Người dùng {user_id} yêu cầu rút {balance}đ.")
        else:
            text = f"⚠️ Số dư tối thiểu để rút là {MIN_WITHDRAW}đ. Hiện bạn có {balance}đ."
    else:
        text = "❓ Không rõ hành động."

    await query.edit_message_text(text=text, reply_markup=menu_keyboard())

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    keep_alive()
    print("Bot đang chạy webhook...")
    await app.bot.set_webhook(WEBHOOK_URL)
    await app.run_webhook(
        listen="0.0.0.0",
        port=80,
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())
