import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import time

BOT_TOKEN = '7915047073:AAFAdbA1dUWazPzfjZT4TJheQcGd8QmYKcA'  # Bot tokenini buraya koy
ADMIN_ID = 8143084360          # Telegram ID'nizi buraya koy

bot = telebot.TeleBot(BOT_TOKEN)

# Dosyalar:
BUTTONS_FILE = 'buttons.json'   # Ana düğmeler ve alt düğmeler için
USERS_FILE = 'users.json'       # Kullanıcı dil ve diğer bilgileri
MESSAGES_FILE = 'messages.json' # Kullanıcı mesajları ve admin yanıtları

# Spam koruma için kullanıcıların son işlem zamanı
user_last_action = {}

# Yardımcı fonksiyonlar
def load_json(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Dil verileri - örnek sadece iki dil için kısa metinler
LANG = {
    "tm": {
        "welcome": "Hoş geldiň!",
        "select_lang": "Dili saýlaň:",
        "lang_tm": "Türkmençe 🇹🇲",
        "lang_ru": "Rusça 🇷🇺",
        "menu_prompt": "Menýudan saýlaň:",
        "admin_only": "Bu buýruk diňe admin üçindir.",
        "spam_warning": "⛔ Köp gezek basdyňyz, az wagt garaşyň.",
        "notify_admin": "📩 Ulanyjy {username} ({user_id}) '{button}' düwmesine basdy.",
        "msg_sent_admin": "✅ Admine habar iberildi, tiz wagtda jogap berler.",
        "admin_panel": "🛠 Admin panel",
        "add_main_btn": "➕ Baş düwme goş",
        "add_sub_btn": "➕ Sub düwme goş",
        "delete_btn": "🗑 Düwmäni aýyr",
        "user_msgs": "📬 Ulanyjylardan gelen habarlar",
        "reply": "✉ Jogap ber",
        "broadcast": "📢 Bildiriş ugrat",
        "stats": "📊 Statistikalar",
        "block_spam": "⛔ Spamlardan gorag",
        "enter_main_btn": "➕ Täze baş düwmäniň adyny ýazyň:",
        "enter_sub_btn_main": "📌 Haysy baş düwmä sub goşmaly? Adyny ýazyň:",
        "enter_sub_btn_name": "✏ Sub düwmäniň adyny ýazyň:",
        "enter_sub_btn_text": "💬 Sub düwmäniň ýazgyny ýazyň:",
        "enter_delete_btn": "🗑 Pozmaly düwmäniň adyny ýazyň:",
        "no_such_button": "❌ Düwmäni tapyp bolmady.",
        "already_exists": "⚠ Bu ad bilen düwme eýýäm bar.",
    },
    "ru": {
        "welcome": "Добро пожаловать!",
        "select_lang": "Выберите язык:",
        "lang_tm": "Туркменский 🇹🇲",
        "lang_ru": "Русский 🇷🇺",
        "menu_prompt": "Выберите из меню:",
        "admin_only": "Эта команда доступна только администратору.",
        "spam_warning": "⛔ Слишком много нажатий, подождите немного.",
        "notify_admin": "📩 Пользователь {username} ({user_id}) нажал на кнопку '{button}'.",
        "msg_sent_admin": "✅ Сообщение отправлено администратору, скоро ответят.",
        "admin_panel": "🛠 Админ панель",
        "add_main_btn": "➕ Добавить главную кнопку",
        "add_sub_btn": "➕ Добавить под кнопку",
        "delete_btn": "🗑 Удалить кнопку",
        "user_msgs": "📬 Сообщения от пользователей",
        "reply": "✉ Ответить",
        "broadcast": "📢 Отправить объявление",
        "stats": "📊 Статистика",
        "block_spam": "⛔ Защита от спама",
        "enter_main_btn": "➕ Введите название новой главной кнопки:",
        "enter_sub_btn_main": "📌 Для какой главной кнопки добавить под кнопку? Введите название:",
        "enter_sub_btn_name": "✏ Введите название под кнопки:",
        "enter_sub_btn_text": "💬 Введите текст под кнопки:",
        "enter_delete_btn": "🗑 Введите название кнопки для удаления:",
        "no_such_button": "❌ Кнопка не найдена.",
        "already_exists": "⚠ Кнопка с таким именем уже существует.",
    }
}

# Kullanıcının dilini al (varsayılan tm)
def get_user_lang(user_id):
    users = load_json(USERS_FILE)
    return users.get(str(user_id), {}).get('lang', 'tm')

# Dil metnini al
def tr(user_id, key):
    lang = get_user_lang(user_id)
    return LANG.get(lang, LANG['tm']).get(key, '')

# Spam koruması
def can_proceed(user_id):
    now = time.time()
    last = user_last_action.get(user_id, 0)
    if now - last < 5:
        return False
    user_last_action[user_id] = now
    return True

# Dil seçimi için inline klavye
def lang_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("Türkmençe 🇹🇲", callback_data="setlang_tm"),
        InlineKeyboardButton("Русский 🇷🇺", callback_data="setlang_ru")
    )
    return markup

# Ana menü düğmeleri oluştur
def main_menu_markup(user_id):
    buttons = load_json(BUTTONS_FILE)
    markup = InlineKeyboardMarkup()
    for main_btn in buttons.keys():
        markup.add(InlineKeyboardButton(main_btn, callback_data=f"main_{main_btn}"))
    return markup

# Sub menü düğmeleri oluştur
def sub_menu_markup(main_btn):
    buttons = load_json(BUTTONS_FILE)
    markup = InlineKeyboardMarkup()
    for sub_btn in buttons.get(main_btn, {}).keys():
        markup.add(InlineKeyboardButton(sub_btn, callback_data=f"sub_{main_btn}_{sub_btn}"))
    return markup

# Başlangıç
@bot.message_handler(commands=['start'])
def start_handler(m):
    user_id = m.from_user.id
    users = load_json(USERS_FILE)
    if str(user_id) not in users or 'lang' not in users[str(user_id)]:
        bot.send_message(user_id, "Dili saýlaň / Выберите язык:", reply_markup=lang_keyboard())
    else:
        bot.send_message(user_id, f"{tr(user_id, 'welcome')}\n👤 @{m.from_user.username} | ID: {user_id}", reply_markup=main_menu_markup(user_id))

# Dil seçimi callback
@bot.callback_query_handler(func=lambda c: c.data.startswith('setlang_'))
def lang_setter(c):
    lang_code = c.data.split('_')[1]
    users = load_json(USERS_FILE)
    users[str(c.from_user.id)] = {'lang': lang_code}
    save_json(USERS_FILE, users)
    bot.answer_callback_query(c.id, "Dil saýlandy / Язык выбран")
    bot.send_message(c.from_user.id, f"{tr(c.from_user.id, 'welcome')}\n👤 @{c.from_user.username} | ID: {c.from_user.id}", reply_markup=main_menu_markup(c.from_user.id))

# Ana düğme basıldığında
@bot.callback_query_handler(func=lambda c: c.data.startswith('main_'))
def main_button_handler(c):
    if not can_proceed(c.from_user.id):
        bot.answer_callback_query(c.id, tr(c.from_user.id, 'spam_warning'))
        return

    main_btn = c.data[5:]
    markup = sub_menu_markup(main_btn)
    if not markup.keyboard:
        bot.answer_callback_query(c.id, "⚠ Bu düwme üçin sub düwme ýok.")
        return
    bot.send_message(c.from_user.id, f"🔽 {main_btn}", reply_markup=markup)

# Sub düğme basıldığında
@bot.callback_query_handler(func=lambda c: c.data.startswith('sub_'))
def sub_button_handler(c):
    if not can_proceed(c.from_user.id):
        bot.answer_callback_query(c.id, tr(c.from_user.id, 'spam_warning'))
        return

    parts = c.data.split('_')
    main_btn = parts[1]
    sub_btn = parts[2]
    buttons = load_json(BUTTONS_FILE)
    text = buttons.get(main_btn, {}).get(sub_btn, "⚠ Bu düwme üçin ýazgy ýok.")

    bot.send_message(c.from_user.id, f"{text}\n\n👤 @{c.from_user.username} | ID: {c.from_user.id}")

    # Admina bildirim gönder
    bot.send_message(ADMIN_ID, LANG[get_user_lang(ADMIN_ID)]['notify_admin'].format(
        username=c.from_user.username or "NoUsername",
        user_id=c.from_user.id,
        button=sub_btn
    ))

    # Kullanıcıya bilgi mesajı
    bot.answer_callback_query(c.id, tr(c.from_user.id, 'msg_sent_admin'))

# Admin paneli - basit örnek (geliştirilebilir)
@bot.message_handler(commands=['panel'])
def admin_panel(m):
    if m.from_user.id != ADMIN_ID:
        bot.reply_to(m, tr(m.from_user.id, 'admin_only'))
        return

    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(LANG['tm']['add_main_btn'], callback_data="admin_add_main"),
        InlineKeyboardButton(LANG['tm']['add_sub_btn'], callback_data="admin_add_sub"),
        InlineKeyboardButton(LANG['tm']['delete_btn'], callback_data="admin_delete"),
    )
    markup.row(
        InlineKeyboardButton(LANG['tm']['user_msgs'], callback_data="admin_user_msgs"),
        InlineKeyboardButton(LANG['tm']['broadcast'], callback_data="admin_broadcast"),
    )
    bot.send_message(m.chat.id, LANG['tm']['admin_panel'], reply_markup=markup)

# Burada admin callback handler eklenmeli
# ... (admin için ek özellikler ve işleyiş buraya eklenmeli)

# Botu başlat
print("Bot başladı...")
bot.infinity_polling()
