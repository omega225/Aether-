import os
import threading
import requests
import telebot
from telebot import types
from flask import Flask, render_template, jsonify

# --- CONFIG ---
API_TOKEN = '8965863331:AAGbI8j6omcDJLKXyPZt1sw4Aiz6_FwVgQY'
# IMPORTANT: When you deploy, Render gives you a URL. Put it here.
WEBAPP_URL = 'https://your-app-name.onrender.com' 

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚀 LAUNCH AETHER V7", web_app=types.WebAppInfo(url=WEBAPP_URL)))
    bot.send_message(message.chat.id, "<b>SYSTEM ARMED.</b>\nPress below to view Future Projection.", parse_mode="HTML", reply_markup=markup)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/vector/<pair>')
def get_vector(pair):
    try:
        # Yahoo Finance API
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{pair}?interval=1m&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers).json()
        
        result = response['chart']['result'][0]
        indicators = result['indicators']['quote'][0]
        closes = indicators['close']
        opens = indicators['open']
        
        # Get last valid price
        last_c = next(x for x in reversed(closes) if x is not None)
        last_o = next(x for x in reversed(opens) if x is not None)
        
        force = last_c - last_o
        future = []
        curr = last_c
        
        for i in range(1, 4):
            move = force * (1.2 - (i * 0.1))
            future.append({
                "o": curr, 
                "c": curr + move, 
                "h": curr + move + (abs(move)*0.2), 
                "l": curr - (abs(move)*0.2)
            })
            curr += move
            
        return jsonify({"status": "success", "price": last_c, "future": future, "pair": pair})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

def run_bot():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
