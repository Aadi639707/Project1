import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import google.generativeai as genai

# YAHA APNE TOKENS DALEIN
BOT_TOKEN = '8705783069:AAGAtEen6KY9et_oD0fyN73h1cfrAcEJSaU'
GEMINI_API_KEY = 'AQ.Ab8RN6JQBbLNS5MIn3HTFWku2VQsPDV8tzN360mmLtFKOHmq4g'

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Bhasha (Language) ka Data
text_data = {
    'en': {
        'ask_reason': "Why do you think your account was frozen? Please explain briefly.",
        'wait': "AI is analyzing your reason and crafting the best unban appeal. Please wait... ⏳",
        'final': "✅ **Best Recovery Method / Appeal Message:**\n\nCopy the message below and send it to `@SpamBot` on Telegram:\n\n`{appeal}`\n\n💡 *Tip: If SpamBot gives options, always choose 'This is a mistake' before sending this message.*",
        'error': "Sorry, there was an error connecting to the AI. Please try again later."
    },
    'hi': {
        'ask_reason': "Aapko kya lagta hai aapki ID kis wajah se freeze hui hai? Kripya detail mein batayein.",
        'wait': "AI aapke reason ko analyze kar raha hai aur sabse best unban appeal bana raha hai. Kripya pratiksha karein... ⏳",
        'final': "✅ **Best Recovery Method / Appeal Message:**\n\nNiche diye gaye message ko copy karein aur Telegram par `@SpamBot` ko bhej dein:\n\n`{appeal}`\n\n💡 *Tip: Agar SpamBot par koi option aaye, toh hamesha 'This is a mistake' choose karke yeh message submit karein.*",
        'error': "Maaf kijiyega, AI se connect karne me error aagaya. Kripya thodi der baad try karein."
    },
    'de': {
        'ask_reason': "Warum glauben Sie, dass Ihr Konto eingefroren wurde? Bitte erklären Sie es kurz.",
        'wait': "Die KI analysiert Ihren Grund und erstellt den besten Entsperrungsantrag. Bitte warten... ⏳",
        'final': "✅ **Beste Wiederherstellungsmethode / Beschwerdenachricht:**\n\nKopieren Sie die untenstehende Nachricht und senden Sie sie an `@SpamBot` auf Telegram:\n\n`{appeal}`\n\n💡 *Tipp: Wenn SpamBot Optionen bietet, wählen Sie immer 'Das ist ein Fehler' aus, bevor Sie diese Nachricht senden.*",
        'error': "Entschuldigung, es gab einen Fehler bei der Verbindung zur KI. Bitte versuchen Sie es später noch einmal."
    }
}

# Start Command - Button dikhane ke liye
@bot.message_handler(commands=['start'])
def start_message(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(
        InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"),
        InlineKeyboardButton("Hindi 🇮🇳", callback_data="lang_hi"),
        InlineKeyboardButton("German 🇩🇪", callback_data="lang_de")
    )
    bot.send_message(message.chat.id, "Please select your language / Kripya apni bhasha chunein / Bitte wählen Sie Ihre Sprache:", reply_markup=markup)

# Button click handle karne ke liye
@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def language_selection(call):
    lang_code = call.data.split('_')[1] # en, hi, ya de extract karega
    chat_id = call.message.chat.id
    
    bot.answer_callback_query(call.id) # Button ka loading animation rokne ke liye
    
    msg = bot.send_message(chat_id, text_data[lang_code]['ask_reason'])
    bot.register_next_step_handler(msg, process_reason, lang_code)

# Reason aur AI process karne ke liye
def process_reason(message, lang_code):
    user_reason = message.text
    bot.reply_to(message, text_data[lang_code]['wait'])
    
    try:
        # Prompt jisme strictly likha h ki answer sirf English me dena h
        ai_prompt = (
            "You are an expert Telegram account recovery specialist. "
            f"A user's account got restricted/frozen. They think the reason is: '{user_reason}'. "
            "Write a highly professional, convincing, and polite appeal message for the user to send to Telegram's @SpamBot. "
            "The appeal should acknowledge any genuine mistake gently, promise strict adherence to Telegram's Terms of Service in the future, "
            "and request an immediate unban. Keep it short (max 120 words) and clear. "
            "CRITICAL RULE: The generated appeal message MUST be strictly in ENGLISH ONLY, no matter what language the user's reason is written in."
        )
        
        response = model.generate_content(ai_prompt)
        appeal = response.text.strip()
        
        # Final message dikhana
        final_text = text_data[lang_code]['final'].format(appeal=appeal)
        bot.reply_to(message, final_text, parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, text_data[lang_code]['error'])
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
