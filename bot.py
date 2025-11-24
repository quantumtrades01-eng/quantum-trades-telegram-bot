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
EXPERT_USERNAME = "@qutrades"                        # your expert username
# ===================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ================ LANGUAGE TEXTS ==================
# lang codes: en, hi, ar
TEXT = {
    "en": {
        "choose_lang": "🌐 Please select your language:",
        "lang_set": "✅ Language set to English.",
        "welcome_menu": "Hey {name} 👋\nWelcome to *Quantum Trades AI* – Official Quotex Signals Hub.\n\nChoose how you want to start 👇",
        "btn_free": "📈 Free Signals Channel",
        "btn_vip": "🚀 Join VIP (Free Using Our Link)",
        "btn_how": "ℹ️ How It Works",
        "btn_expert": "🧑‍💻 Talk to Expert",
        "btn_upgrade_vip": "🚀 Upgrade to VIP",
        "btn_main_menu": "🏠 Main Menu",
        "free_signals": (
            "📈 *Free Signals Channel Access*\n\n"
            "You can start with our *Free Signals Channel* and copy trades daily.\n\n"
            "🔹 2–4 quality signals per day\n"
            "🔹 Good to test our accuracy\n"
            "🔹 No fees, no conditions\n\n"
            "👉 Join here:\n{free_link}\n\n"
            "Once you trust the results, upgrade to *VIP* and get\n"
            "*10–15 SureShot signals every day* ⚡"
        ),
        "how_it_works": (
            "ℹ️ *How Our System Works*\n\n"
            "We keep it simple and transparent:\n\n"
            "1️⃣ Create a *new Quotex account* using our official partner link\n"
            "2️⃣ Deposit at least *$50* (recommended to follow VIP signals properly)\n"
            "3️⃣ Send us your *Quotex ID Number*\n"
            "4️⃣ We verify → You get *FREE VIP Access* (no extra fee to us)\n\n"
        ),
        "vip_info": (
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
        ),
        "create_account": (
            "🔗 *Step 1 – Create Your Quotex Account*\n\n"
            "Tap the link below to open your official Quotex signup page:\n\n"
            "{ref_link}\n\n"
            "After creating your account:\n"
            "1️⃣ Deposit at least *$50*\n"
            "2️⃣ Come back here and tap *“I Created & Deposited $50+”*"
        ),
        "ask_id": (
            "✅ Great!\n\n"
            "Please send your *Quotex ID Number* now.\n"
            "You can find it in your Quotex profile (example: `45671234`)."
        ),
        "id_submitted": (
            "🔍 Your Quotex ID has been submitted for verification.\n\n"
            "We’ll verify your account and send your *VIP channel access* soon.\n"
            "Stay ready – you might catch today's VIP entries ⚡"
        ),
        "need_help_deposit": (
            "💳 *Need Help With Deposit?*\n\n"
            "Our standard requirement for VIP is a *$50 starting balance*, because below that\n"
            "it’s harder to follow risk management properly.\n\n"
            "If this amount is heavy for you right now,\n"
            "send us a message with:\n"
            "• Your current budget\n"
            "• What you can realistically start with\n\n"
            "One of our experts will review your case and try to guide you with a *custom plan* "
            "so you can still start safely ✅"
        ),
        "talk_to_expert": (
            "🧑‍💻 *Talk to a Human Expert*\n\n"
            "An expert will contact you shortly.\n\n"
            f"Meanwhile, you can *directly DM our expert* here:\n{EXPERT_USERNAME}\n\n"
            "You can also type your questions here in chat.\n"
            "If you ever want to go back to the main menu, just type /menu or /start."
        ),
        "thanks_message": (
            "Thanks for your message, {name} ✅\n\n"
            "Here’s the menu, choose what you want to do next 👇"
        ),
        "back_to_menu": "Main menu opened 👇",
    },
    "hi": {
        "choose_lang": "🌐 कृपया अपनी भाषा चुनें:",
        "lang_set": "✅ भाषा हिंदी चुनी गई है।",
        "welcome_menu": "नमस्ते {name} 👋\n*Quantum Trades AI* में आपका स्वागत है – Official Quotex Signals Hub.\n\nशुरू करने के लिए नीचे से एक विकल्प चुनें 👇",
        "btn_free": "📈 फ्री सिग्नल चैनल",
        "btn_vip": "🚀 VIP जॉइन करें (हमारे लिंक से फ्री)",
        "btn_how": "ℹ️ ये कैसे काम करता है?",
        "btn_expert": "🧑‍💻 एक्सपर्ट से बात करें",
        "btn_upgrade_vip": "🚀 VIP में अपग्रेड करें",
        "btn_main_menu": "🏠 मुख्य मेनू",
        "free_signals": (
            "📈 *फ्री सिग्नल चैनल एक्सेस*\n\n"
            "आप हमारे *फ्री सिग्नल चैनल* से शुरू कर सकते हैं और रोज़ ट्रेड कॉपी कर सकते हैं।\n\n"
            "🔹 रोज़ 2–4 क्वालिटी सिग्नल\n"
            "🔹 हमारी accuracy टेस्ट करने के लिए बेस्ट\n"
            "🔹 कोई फीस नहीं, कोई शर्त नहीं\n\n"
            "👉 यहाँ जॉइन करें:\n{free_link}\n\n"
            "जब आपको रिज़ल्ट पर भरोसा हो जाए, तब *VIP* में अपग्रेड करें और\n"
            "रोज़ *10–15 SureShot सिग्नल* पाएँ ⚡"
        ),
        "how_it_works": (
            "ℹ️ *ये कैसे काम करता है?*\n\n"
            "हम सब कुछ simple और transparent रखते हैं:\n\n"
            "1️⃣ हमारी official partner लिंक से *नया Quotex अकाउंट* बनाएँ\n"
            "2️⃣ कम से कम *$50* डिपोज़िट करें\n"
            "3️⃣ अपना *Quotex ID Number* हमें भेजें\n"
            "4️⃣ हम verify करेंगे → और आपको *फ्री VIP एक्सेस* देंगे (हम कोई extra fees नहीं लेते)\n\n"
        ),
        "vip_info": (
            "🚀 *VIP सिर्फ serious ट्रेडर्स के लिए*\n\n"
            "हमारे *VIP Quotex Group* में आपको मिलता है:\n\n"
            "✅ रोज़ 10–15 SureShot सिग्नल\n"
            "✅ High-probability setups\n"
            "✅ News & volatility filter (random entries नहीं)\n"
            "✅ Risk & money management गाइड\n"
            "✅ Priority 1:1 सपोर्ट\n"
            "✅ *$50+* अकाउंट के लिए डिजाइन किया गया\n\n"
            "💰 *हम कोई extra fees नहीं लेते*\n"
            "आपको बस ये करना है:\n\n"
            "1️⃣ हमारे लिंक से नया Quotex अकाउंट\n"
            "2️⃣ कम से कम *$50 डिपॉज़िट*\n"
            "3️⃣ अपना *Quotex ID* हमें भेजें\n\n"
            "इसके बाद → हम आपका *VIP चैनल एक्सेस* अनलॉक कर देंगे 🎯\n\n"
            "आज का VIP session मिस मत करें – कुछ बेहतरीन setups वहीं शेयर होते हैं।"
        ),
        "create_account": (
            "🔗 *स्टेप 1 – Quotex अकाउंट बनाइए*\n\n"
            "नीचे दिए गए लिंक से अपना official Quotex signup पेज खोलें:\n\n"
            "{ref_link}\n\n"
            "अकाउंट बनाने के बाद:\n"
            "1️⃣ कम से कम *$50* डिपॉज़िट करें\n"
            "2️⃣ वापस यहाँ आएँ और *“I Created & Deposited $50+”* पर क्लिक करें"
        ),
        "ask_id": (
            "✅ बढ़िया!\n\n"
            "अब अपना *Quotex ID Number* भेजिए।\n"
            "आप इसे Quotex profile में देख सकते हैं (जैसे: `45671234`)."
        ),
        "id_submitted": (
            "🔍 आपका Quotex ID verification के लिए भेज दिया गया है।\n\n"
            "हम verify करके आपको *VIP चैनल एक्सेस* भेज देंगे।\n"
            "तैयार रहिए – हो सकता है आज ही के VIP entries आप पकड़ लें ⚡"
        ),
        "need_help_deposit": (
            "💳 *डिपॉज़िट में मदद चाहिए?*\n\n"
            "VIP के लिए हमारा standard requirement *$50 starting balance* है, क्योंकि इससे कम पर\n"
            "proper risk management follow करना मुश्किल हो जाता है।\n\n"
            "अगर ये amount आपके लिए heavy लग रहा है,\n"
            "तो हमें ये details भेजें:\n"
            "• आपका current budget\n"
            "• आप realistically कितना start कर सकते हैं\n\n"
            "हमारे experts आपकी situation देखकर आपके लिए *custom plan* बनाने की कोशिश करेंगे ✅"
        ),
        "talk_to_expert": (
            "🧑‍💻 *एक्सपर्ट से बात करें*\n\n"
            "हमारा एक्सपर्ट जल्दी ही आपसे contact करेगा।\n\n"
            f"जब तक आप wait कर रहे हैं, आप सीधे हमारे expert को यहाँ DM कर सकते हैं:\n{EXPERT_USERNAME}\n\n"
            "आप अपने सवाल यहाँ भी टाइप कर सकते हैं।\n"
            "कभी भी main menu पर वापस जाने के लिए /menu या /start लिखें।"
        ),
        "thanks_message": (
            "थैंक्यू {name} ✅\n\n"
            "नीचे से अपना अगला स्टेप चुनें 👇"
        ),
        "back_to_menu": "मुख्य मेनू खुल गया है 👇",
    },
    "ar": {
        "choose_lang": "🌐 من فضلك اختر لغتك:",
        "lang_set": "✅ تم اختيار اللغة العربية.",
        "welcome_menu": "مرحباً {name} 👋\nمرحباً بك في *Quantum Trades AI* – مركز إشارات Quotex الرسمي.\n\nاختر طريقة البدء 👇",
        "btn_free": "📈 قناة الإشارات المجانية",
        "btn_vip": "🚀 انضم إلى VIP (مجاناً عبر رابطنا)",
        "btn_how": "ℹ️ كيف يعمل النظام؟",
        "btn_expert": "🧑‍💻 التحدث مع خبير",
        "btn_upgrade_vip": "🚀 الترقية إلى VIP",
        "btn_main_menu": "🏠 القائمة الرئيسية",
        "free_signals": (
            "📈 *الوصول إلى قناة الإشارات المجانية*\n\n"
            "يمكنك البدء من *قناتنا المجانية* ونسخ الصفقات يومياً.\n\n"
            "🔹 2–4 إشارات قوية يومياً\n"
            "🔹 ممتازة لاختبار دقة النتائج\n"
            "🔹 بدون رسوم أو شروط\n\n"
            "👉 انضم من هنا:\n{free_link}\n\n"
            "عندما تثق في النتائج، يمكنك الترقية إلى *VIP* للحصول على\n"
            "*10–15 إشارة مضمونة يومياً* ⚡"
        ),
        "how_it_works": (
            "ℹ️ *كيف يعمل نظامنا؟*\n\n"
            "نحافظ على الأمور بسيطة وشفافة:\n\n"
            "1️⃣ أنشئ حساب Quotex جديد باستخدام *رابط الشريك الرسمي* الخاص بنا\n"
            "2️⃣ أودع على الأقل *50 دولاراً*\n"
            "3️⃣ أرسل لنا *رقم حساب Quotex (ID)* الخاص بك\n"
            "4️⃣ نتحقق → ونمنحك *وصول VIP مجاناً* (لا ندفعنا أي رسوم إضافية)\n\n"
        ),
        "vip_info": (
            "🚀 *VIP مخصص للمتداولين الجادين فقط*\n\n"
            "داخل *مجموعة VIP على Quotex* ستحصل على:\n\n"
            "✅ 10–15 إشارة يومية عالية الاحتمال\n"
            "✅ صفقات مختارة بعناية\n"
            "✅ تصفية الأخبار والتقلبات (لا دخول عشوائي)\n"
            "✅ إرشاد لإدارة رأس المال والمخاطر\n"
            "✅ أولوية دعم خاص 1:1\n"
            "✅ مصمم لحسابات تبدأ من *50 دولاراً فأكثر*\n\n"
            "💰 *لا توجد رسوم إضافية لنا*\n"
            "فقط قم بـ:\n\n"
            "1️⃣ فتح حساب Quotex جديد برابطنا\n"
            "2️⃣ إيداع *50 دولاراً* على الأقل\n"
            "3️⃣ إرسال *رقم حساب Quotex (ID)* لنا\n\n"
            "بعد ذلك → نمنحك *وصول قناة VIP* 🎯\n\n"
            "لا تضيّع جلسة VIP اليوم – أفضل الفرص هناك."
        ),
        "create_account": (
            "🔗 *الخطوة 1 – إنشاء حساب Quotex*\n\n"
            "اضغط على الرابط أدناه لفتح صفحة التسجيل الرسمية:\n\n"
            "{ref_link}\n\n"
            "بعد إنشاء الحساب:\n"
            "1️⃣ أودع على الأقل *50 دولاراً*\n"
            "2️⃣ عد إلى هنا واضغط *“I Created & Deposited $50+”*"
        ),
        "ask_id": (
            "✅ ممتاز!\n\n"
            "الآن أرسل لنا *رقم حساب Quotex (ID)* الخاص بك.\n"
            "يمكنك إيجاده داخل ملفك الشخصي في Quotex (مثال: `45671234`)."
        ),
        "id_submitted": (
            "🔍 تم إرسال رقم حسابك للمراجعة.\n\n"
            "سنقوم بالتحقق ومن ثم نرسل لك *وصول قناة VIP*.\n"
            "كن مستعداً – قد تلحق بإشارات اليوم VIP ⚡"
        ),
        "need_help_deposit": (
            "💳 *تحتاج مساعدة في الإيداع؟*\n\n"
            "الحد الأدنى القياسي لبدء VIP هو *50 دولاراً*، لأن أقل من ذلك يجعل\n"
            "إدارة المخاطر بشكل صحيح أمراً صعباً.\n\n"
            "إذا كان هذا المبلغ كبيراً عليك الآن، أرسل لنا:\n"
            "• ميزانيتك الحالية\n"
            "• المبلغ الذي يمكنك البدء به فعلياً\n\n"
            "سيقوم خبيرنا بمراجعة حالتك ومحاولة إعطائك *خطة خاصة تناسبك* ✅"
        ),
        "talk_to_expert": (
            "🧑‍💻 *التحدث مع خبير بشري*\n\n"
            "سيقوم الخبير بالتواصل معك قريباً.\n\n"
            f"في هذه الأثناء، يمكنك مراسلة خبيرنا مباشرة هنا:\n{EXPERT_USERNAME}\n\n"
            "يمكنك أيضاً كتابة أسئلتك هنا في المحادثة.\n"
            "للعودة إلى القائمة الرئيسية في أي وقت، اكتب /menu أو /start."
        ),
        "thanks_message": (
            "شكراً لك {name} ✅\n\n"
            "اختر خطوتك التالية من الأسفل 👇"
        ),
        "back_to_menu": "تم فتح القائمة الرئيسية 👇",
    },
}

LANG_LABELS = {
    "en": "English 🇺🇸",
    "hi": "हिन्दी 🇮🇳",
    "ar": "العربية 🇦🇪",
}


def get_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("lang", "en")


def set_lang(context: ContextTypes.DEFAULT_TYPE, lang: str):
    context.user_data["lang"] = lang


# ================ KEYBOARDS ==================
def language_keyboard():
    keyboard = [
        [InlineKeyboardButton(LANG_LABELS["en"], callback_data="lang_en")],
        [InlineKeyboardButton(LANG_LABELS["hi"], callback_data="lang_hi")],
        [InlineKeyboardButton(LANG_LABELS["ar"], callback_data="lang_ar")],
    ]
    return InlineKeyboardMarkup(keyboard)


def main_menu_keyboard(lang: str):
    k = TEXT[lang]
    keyboard = [
        [InlineKeyboardButton(k["btn_free"], callback_data="free_signals")],
        [InlineKeyboardButton(k["btn_vip"], callback_data="join_vip")],
        [InlineKeyboardButton(k["btn_how"], callback_data="how_it_works")],
        [InlineKeyboardButton(k["btn_expert"], callback_data="talk_expert")],
    ]
    return InlineKeyboardMarkup(keyboard)


def free_signals_keyboard(lang: str):
    k = TEXT[lang]
    keyboard = [
        [InlineKeyboardButton(k["btn_upgrade_vip"], callback_data="join_vip")],
        [InlineKeyboardButton(k["btn_main_menu"], callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def how_it_works_keyboard_markup(lang: str):
    k = TEXT[lang]
    keyboard = [
        [InlineKeyboardButton(k["btn_vip"], callback_data="join_vip")],
        [InlineKeyboardButton(k["btn_free"], callback_data="free_signals")],
        [InlineKeyboardButton(k["btn_main_menu"], callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def vip_menu_keyboard(lang: str):
    k = TEXT[lang]
    keyboard = [
        [InlineKeyboardButton("🔗 Create Quotex Account", callback_data="create_account")],
        [InlineKeyboardButton("✅ I Created & Deposited $50+", callback_data="deposited_50")],
        [InlineKeyboardButton("💳 I Need Help With Deposit", callback_data="need_help_deposit")],
        [InlineKeyboardButton(k["btn_free"], callback_data="free_signals")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ========= Helper: send admin notification + relay map =========
async def notify_admin_from_user_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    header_text: str,
    relay: bool = True,
):
    """
    Forward the user's original message to admin + send summary.
    Store mapping so reply from admin can be relayed back.
    """
    user = update.effective_user
    msg = update.message
    relay_map: Dict[int, int] = context.application.bot_data.setdefault("relay_map", {})

    # Forward original message (clickable profile)
    fwd = await msg.forward(chat_id=ADMIN_CHAT_ID)
    if relay:
        relay_map[fwd.message_id] = user.id

    # Send summary message
    info = await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=header_text)
    if relay:
        relay_map[info.message_id] = user.id


async def notify_admin_simple(
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int,
    header_text: str,
    relay: bool = True,
):
    """
    Send only a summary text to admin (no forwarded message),
    still map for relay if needed.
    """
    relay_map: Dict[int, int] = context.application.bot_data.setdefault("relay_map", {})
    info = await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=header_text)
    if relay:
        relay_map[info.message_id] = user_id


# ==================== USER SIDE HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Reset mode to normal when /start
    context.user_data["mode"] = "normal"

    if "lang" not in context.user_data:
        # Ask for language first
        text = (
            "🌐 Please select your language / अपनी भाषा चुनें / اختر لغتك:\n\n"
            f"{LANG_LABELS['en']} | {LANG_LABELS['hi']} | {LANG_LABELS['ar']}"
        )
        await update.message.reply_text(text, reply_markup=language_keyboard())
        return

    lang = get_lang(context)
    t = TEXT[lang]
    name = update.effective_user.first_name
    text = t["welcome_menu"].format(name=name)
    await update.message.reply_text(text, reply_markup=main_menu_keyboard(lang), parse_mode="Markdown")


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # /menu goes to main menu in selected language
    context.user_data["mode"] = "normal"
    lang = get_lang(context)
    t = TEXT[lang]
    name = update.effective_user.first_name
    text = t["welcome_menu"].format(name=name)
    await update.message.reply_text(text, reply_markup=main_menu_keyboard(lang), parse_mode="Markdown")


async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles messages coming from NORMAL USERS (not admin).
    Includes:
    - Quotex ID submission (after deposited_50)
    - Normal text → menu or expert mode
    - Forward to admin with relay mapping
    """
    user = update.effective_user
    msg = update.message.text
    lang = get_lang(context)
    t = TEXT[lang]

    # If user was asked to send their Quotex ID
    if context.user_data.get("waiting_for_id"):
        context.user_data["waiting_for_id"] = False

        header_text = (
            "🔔 New VIP Verification Request\n\n"
            f"User: @{user.username or user.id}\n"
            f"User ID: {user.id}\n"
            f"Quotex ID (claimed, deposited >= $50): {msg}\n\n"
            "Reply to this message to answer this user directly or DM them from the forwarded message above."
        )
        await notify_admin_from_user_message(update, context, header_text, relay=True)

        reply = t["id_submitted"]
        await update.message.reply_text(reply, parse_mode="Markdown", reply_markup=main_menu_keyboard(lang))
        return

    # Check mode: normal vs expert
    mode = context.user_data.get("mode", "normal")

    header_text = (
        "📩 New Message Lead\n\n"
        f"From: @{user.username or user.id}\n"
        f"User ID: {user.id}\n\n"
        f"Message:\n{msg}\n\n"
        "Reply to this message to answer this user directly or DM them from the forwarded message above."
    )
    await notify_admin_from_user_message(update, context, header_text, relay=True)

    if mode == "expert":
        # In expert mode: bot stays mostly silent (no menu spam)
        # You already showed talk_to_expert text once.
        # User & admin now talk, bot just forwards.
        return

    # Normal mode: show menu
    reply = t["thanks_message"].format(name=user.first_name)
    await update.message.reply_text(reply, reply_markup=main_menu_keyboard(lang))


# ==================== ADMIN SIDE HANDLER (RELAY) ====================
async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle messages sent by ADMIN_CHAT_ID.
    If admin replies to a forwarded lead message or summary,
    we send that reply back to the user.
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
            "Please reply directly under a lead notification or forwarded user message.",
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

    # Language selection first
    if data in ("lang_en", "lang_hi", "lang_ar"):
        if data == "lang_en":
            set_lang(context, "en")
        elif data == "lang_hi":
            set_lang(context, "hi")
        else:
            set_lang(context, "ar")

        lang = get_lang(context)
        t = TEXT[lang]
        context.user_data["mode"] = "normal"

        await query.edit_message_text(t["lang_set"])
        name = user.first_name
        text = t["welcome_menu"].format(name=name)
        await query.message.reply_text(text, reply_markup=main_menu_keyboard(lang), parse_mode="Markdown")
        return

    # From here: lang must be set
    lang = get_lang(context)
    t = TEXT[lang]

    # MAIN MENU
    if data == "main_menu":
        context.user_data["mode"] = "normal"
        text = t["welcome_menu"].format(name=user.first_name)
        await query.edit_message_text(text, reply_markup=main_menu_keyboard(lang), parse_mode="Markdown")

    # FREE SIGNALS
    elif data == "free_signals":
        context.user_data["mode"] = "normal"
        text = t["free_signals"].format(free_link=FREE_CHANNEL_LINK)
        await query.edit_message_text(text, reply_markup=free_signals_keyboard(lang), parse_mode="Markdown")

    # HOW IT WORKS
    elif data == "how_it_works":
        context.user_data["mode"] = "normal"
        text = t["how_it_works"]
        await query.edit_message_text(text, reply_markup=how_it_works_keyboard_markup(lang), parse_mode="Markdown")

    # JOIN VIP PAGE
    elif data == "join_vip":
        context.user_data["mode"] = "normal"
        text = t["vip_info"]
        await query.edit_message_text(text, reply_markup=vip_menu_keyboard(lang), parse_mode="Markdown")

    # CREATE ACCOUNT
    elif data == "create_account":
        context.user_data["mode"] = "normal"
        text = t["create_account"].format(ref_link=REFERRAL_LINK)
        await query.edit_message_text(text, reply_markup=vip_menu_keyboard(lang), parse_mode="Markdown")

    # USER CONFIRMED DEPOSIT
    elif data == "deposited_50":
        context.user_data["mode"] = "normal"
        context.user_data["waiting_for_id"] = True
        text = t["ask_id"]
        await query.edit_message_text(text, parse_mode="Markdown")

    # USER NEEDS HELP WITH DEPOSIT
    elif data == "need_help_deposit":
        context.user_data["mode"] = "normal"
        text = t["need_help_deposit"]
        await query.edit_message_text(text, reply_markup=main_menu_keyboard(lang), parse_mode="Markdown")

        # Notify admin
        header_text = (
            "⚠️ Deposit Help Requested\n\n"
            f"User: @{user.username or user.id}\n"
            f"User ID: {user.id}\n"
            "Clicked 'Need Help With Deposit'. Possible low-budget case.\n\n"
            "Reply to this message to answer this user directly."
        )
        await notify_admin_simple(context, user.id, header_text, relay=True)

    # TALK TO EXPERT
    elif data == "talk_expert":
        # Put user in expert mode (bot won't spam menus)
        context.user_data["mode"] = "expert"
        text = t["talk_to_expert"]
        await query.edit_message_text(text, reply_markup=main_menu_keyboard(lang), parse_mode="Markdown")

        # Immediate admin notification
        header_text = (
            "👤 User Wants to Talk to Expert\n\n"
            f"User: @{user.username or user.id}\n"
            f"User ID: {user.id}\n"
            "They clicked 'Talk to Expert'. They may DM you directly or write here.\n\n"
            "Reply to this message to answer this user through the bot, "
            "or DM them from any forwarded message when they send text."
        )
        await notify_admin_simple(context, user.id, header_text, relay=True)


# ==================== ROUTER ====================
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


# ==================== MAIN ====================
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # init relay map
    application.bot_data["relay_map"] = {}

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu_command))
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
