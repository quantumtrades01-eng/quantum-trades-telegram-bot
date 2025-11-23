import os
import logging
from typing import Dict

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ================ CONFIG FROM ENV ==================
BOT_TOKEN = os.environ["BOT_TOKEN"]              # from Render env
ADMIN_CHAT_ID = int(os.environ["ADMIN_CHAT_ID"]) # your Telegram ID

REFERRAL_LINK = os.environ["REFERRAL_LINK"]          # your Quotex ref link
FREE_CHANNEL_LINK = os.environ["FREE_CHANNEL_LINK"]  # your free signals channel link
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")          # set on Render
# ===================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


# ========= Helper: send admin notification + store relay mapping =========
async def send_admin_notification(
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    user_id: int,
    relay: bool = True,
):
    """
    Send a message to ADMIN_CHAT_ID.
    If relay=True, we store which user this admin message belongs to,
    so admin can reply and bot will forward back to that user.
    """
    if relay:
        msg = await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)
        relay_map: Dict[int, int] = context.application.bot_data.setdefault("relay_map", {})
        relay_map[msg.message_id] = user_id
    else:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)


# ==================== Keyboards =====================
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📈 Free Signals Channel", callback_data="free_signals")],
        [InlineKeyboardButton("🚀 Join VIP (Free Using Our Link)", callback_data="join_vip")],
        [InlineKeyboardButton("ℹ️ How It Works", callback_data="how_it_works")],
        [InlineKeyboardButton("🧑‍💻 Talk to Expert", callback_data="talk_expert")],
    ]
    return InlineKeyboardMarkup(keyboard)


def vip_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔗 Create Quotex Account", callback_data="create_account")],
        [InlineKeyboardButton("✅ I Created & Deposited $50+", callback_data="deposited_50")],
        [InlineKeyboardButton("💳 I Need Help With Deposit", callback_data="need_help_deposit")],
        [InlineKeyboardButton("📈 Go to Free Signals", callback_data="free_signals")],
    ]
    return InlineKeyboardMarkup(keyboard)


def free_signals_keyboard():
    keyboard = [
        [InlineKeyboardButton("🚀 Upgrade to VIP", callback_data="join_vip")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def how_it_works_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔐 Get VIP Access", callback_data="join_vip")],
        [InlineKeyboardButton("📈 Go to Free Signals", callback_data="free_signals")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(how_it_works_keyboard)


# ==================== USER SIDE HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        f"Hey {user.first_name} 👋\n"
        "Welcome to *Quantum Trades AI* – Official Quotex Signals Hub.\n\n"
        "Choose how you want to start 👇"
    )
    await update.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")


async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles messages coming from NORMAL USERS (not admin).
    Includes:
    - Quotex ID submission (after deposited_50)
    - Normal text → send menu
    - Forward to admin with relay mapping
    """
    user = update.effective_user
    msg = update.message.text

    # If user was asked to send their Quotex ID
    if context.user_data.get("waiting_for_id"):
        context.user_data["waiting_for_id"] = False

        # Notify admin with relay support (so you can reply)
        admin_text = (
            "🔔 New VIP Verification Request\n\n"
            f"User: @{user.username or user.id}\n"
            f"User ID: {user.id}\n"
            f"Quotex ID (claimed, deposited >= $50): {msg}\n\n"
            "Reply to this message to answer this user directly."
        )
        await send_admin_notification(context, admin_text, user.id, relay=True)

        # Confirm to user
        reply = (
            "🔍 Your Quotex ID has been submitted for verification.\n\n"
            "We’ll verify your account and send your *VIP channel access* soon.\n"
            "Stay ready – you might catch today's VIP entries ⚡"
        )
        await update.message.reply_text(reply, parse_mode="Markdown", reply_markup=main_menu_keyboard())
        return

    # Generic message path – treat as normal lead + show menu
    admin_text = (
        "📩 New Message Lead\n\n"
        f"From: @{user.username or user.id}\n"
        f"User ID: {user.id}\n\n"
        f"Message:\n{msg}\n\n"
        "Reply to this message to answer this user directly."
    )
    await send_admin_notification(context, admin_text, user.id, relay=True)

    reply = (
        f"Thanks for your message, {user.first_name} ✅\n\n"
        "Here’s the menu, choose what you want to do next 👇"
    )
    await update.message.reply_text(reply, reply_markup=main_menu_keyboard())


# ==================== ADMIN SIDE HANDLER (RELAY) ====================
async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle messages sent by ADMIN_CHAT_ID.
    If admin replies to a forwarded lead message, we send that reply back to the user.
    """
    msg = update.message
    relay_map: Dict[int, int] = context.application.bot_data.setdefault("relay_map", {})

    # Must be a reply to one of the bot's admin notifications
    if not msg.reply_to_message:
        await msg.reply_text(
            "To reply to a user, please *reply to one of the lead messages* I sent you.",
            parse_mode="Markdown",
        )
        return

    target_user_id = relay_map.get(msg.reply_to_message.message_id)
    if not target_user_id:
        await msg.reply_text(
            "I can't find which user this message belongs to.\n"
            "Please reply directly under a lead notification message.",
        )
        return

    # Forward admin's reply text to the target user
    try:
        await context.bot.send_message(
            chat_id=target_user_id,
            text=msg.text,
        )
        await msg.reply_text("✅ Sent to user.")
    except Exception as e:
        logging.exception("Failed to send admin reply to user")
        await msg.reply_text(f"❌ Failed to send message to user: {e}")


# ==================== BUTTON HANDLER ====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user = query.from_user

    await query.answer()

    # MAIN MENU
    if data == "main_menu":
        text = (
            f"Hey {user.first_name} 👋\n"
            "Welcome back to *Quantum Trades AI*.\n\n"
            "Choose how you want to continue 👇"
        )
        await query.edit_message_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

    # FREE SIGNALS
    elif data == "free_signals":
        text = (
            "📈 *Free Signals Channel Access*\n\n"
            "You can start with our *Free Signals Channel* and copy trades daily.\n\n"
            "🔹 2–4 quality signals per day\n"
            "🔹 Good to test our accuracy\n"
            "🔹 No fees, no conditions\n\n"
            f"👉 Join here: {FREE_CHANNEL_LINK}\n\n"
            "Once you trust the results, upgrade to *VIP* and get\n"
            "*10–15 SureShot signals every day* ⚡"
        )
        await query.edit_message_text(text, reply_markup=free_signals_keyboard(), parse_mode="Markdown")

    # HOW IT WORKS
    elif data == "how_it_works":
        text = (
            "ℹ️ *How Our System Works*\n\n"
            "We keep it simple and transparent:\n\n"
            "1️⃣ Create a *new Quotex account* using our official partner link\n"
            "2️⃣ Deposit at least *$50* (recommended to follow VIP signals properly)\n"
            "3️⃣ Send us your *Quotex ID Number*\n"
            "4️⃣ We verify → You get *FREE VIP Access* (no extra fee to us)\n\n"
            "We earn commission directly from Quotex, so *you don’t pay us anything extra* "
            "for VIP signals. It’s a pure *win–win* partnership 🤝\n\n"
            "⚠ Trading involves risk. Only use money you can afford to trade."
        )
        await query.edit_message_text(text, reply_markup=how_it_works_keyboard(), parse_mode="Markdown")

    # JOIN VIP PAGE
    elif data == "join_vip":
        text = (
            "🚀 *VIP Access – For Serious Traders Only*\n\n"
            "Inside our *VIP Quotex Group* you get:\n\n"
            "✅ 10–15 SureShot signals daily\n"
            "✅ Handpicked high-probability setups\n"
            "✅ News & volatility filters (no random entries)\n"
            "✅ Risk & money management guidance\n"
            "✅ Priority 1:1 support on DM\n"
            "✅ Designed for accounts starting from *$50+*\n\n"
            "💰 *No extra fees to us*\n"
            "You just need:\n\n"
            "1️⃣ A new Quotex account via *our* link\n"
            "2️⃣ Minimum *$50 deposit* in that account\n"
            "3️⃣ Share your *Quotex ID* with us\n\n"
            "After that → we unlock your *VIP channel access* 🎯\n\n"
            "Don’t miss today’s VIP session – some of the best setups are shared there."
        )
        await query.edit_message_text(text, reply_markup=vip_menu_keyboard(), parse_mode="Markdown")

    # CREATE ACCOUNT
    elif data == "create_account":
        text = (
            "🔗 *Step 1 – Create Your Quotex Account*\n\n"
            "Tap the link below to open your official Quotex signup page:\n\n"
            f"{REFERRAL_LINK}\n\n"
            "After creating your account:\n"
            "1️⃣ Deposit at least *$50*\n"
            "2️⃣ Come back here and tap *“I Created & Deposited $50+”*"
        )
        await query.edit_message_text(text, reply_markup=vip_menu_keyboard(), parse_mode="Markdown")

    # USER CONFIRMED DEPOSIT
    elif data == "deposited_50":
        context.user_data["waiting_for_id"] = True
        text = (
            "✅ Great!\n\n"
            "Please send your *Quotex ID Number* now.\n"
            "You can find it in your Quotex profile (example: `45671234`)."
        )
        await query.edit_message_text(text, parse_mode="Markdown")

    # USER NEEDS HELP WITH DEPOSIT
    elif data == "need_help_deposit":
        text = (
            "💳 *Need Help With Deposit?*\n\n"
            "Our standard requirement for VIP is a *$50 starting balance*, because below that\n"
            "it’s harder to follow risk management properly.\n\n"
            "If this amount is heavy for you right now,\n"
            "send us a message with:\n"
            "• Your current budget\n"
            "• What you can realistically start with\n\n"
            "One of our experts will review your case and try to guide you with a *custom plan* "
            "so you can still start safely ✅"
        )
        await query.edit_message_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

        # Notify admin
        admin_text = (
            "⚠️ Deposit Help Requested\n\n"
            f"User: @{user.username or user.id}\n"
            f"User ID: {user.id}\n"
            "Clicked 'Need Help With Deposit'. Possible low-budget case.\n\n"
            "Reply to this message to answer this user directly."
        )
        await send_admin_notification(context, admin_text, user.id, relay=True)

    # TALK TO EXPERT
    elif data == "talk_expert":
        text = (
            "🧑‍💻 *Talk to a Human Expert*\n\n"
            "Type your question in one message below\n"
            "(for example: `I have $60, how should I start?`).\n\n"
            "Our team will reply to you personally as soon as possible."
        )
        await query.edit_message_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

        admin_text = (
            "👤 User Wants to Talk to Expert\n\n"
            f"User: @{user.username or user.id}\n"
            f"User ID: {user.id}\n"
            "They clicked 'Talk to Expert'. Watch for their next message.\n\n"
            "Reply to this message to answer this user directly."
        )
        await send_admin_notification(context, admin_text, user.id, relay=True)


# ==================== MAIN ====================
async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Single MessageHandler entry:
    - If admin -> handle_admin_message
    - If normal user -> handle_user_message
    """
    user = update.effective_user
    if user.id == ADMIN_CHAT_ID:
        await handle_admin_message(update, context)
    else:
        await handle_user_message(update, context)


def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # init relay map
    application.bot_data["relay_map"] = {}

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_router))

    # On Render we ALWAYS use webhook
    port = int(os.environ.get("PORT", "10000"))
    if not WEBHOOK_URL:
        raise RuntimeError("WEBHOOK_URL environment variable is not set")

    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}",
    )


if __name__ == "__main__":
    main()
