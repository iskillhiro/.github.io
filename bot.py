from flask import Flask
from flask import request
from threading import Thread
import time
import requests

app = Flask('')


@app.route('/')
def home():
  return "I'm alive"


def run():
  app.run(host='0.0.0.0', port=80)


def keep_alive():
  t = Thread(target=run)
  t.start()


import telebot
from telebot import types
from facts import get_random_fact
from main import get_forecast
from quotes import get_random_fishing_quote
# Устанавливаем токен вашего бота
TOKEN = '6505585614:AAFHWBwScjaNjzxtu7ZxQmTAwQ2tfVRQJmM'
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn_weather = types.KeyboardButton('Прогноз🌤️')
btn_fact = types.KeyboardButton('Факт💡')
btn_quote = types.KeyboardButton('Цитата🎣')
markup.add(btn_weather, btn_fact, btn_quote)
# Создаем объект бота
bot = telebot.TeleBot(TOKEN)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, get_forecast(), reply_markup=markup)

@bot.message_handler(content_types="text")
def get_content(message):
    if message.text == 'Прогноз🌤️':
        bot.send_message(message.chat.id, get_forecast(), reply_markup=markup)
    if message.text == 'Факт💡':
        bot.send_message(message.chat.id, get_random_fact(), reply_markup=markup)
    if message.text == 'Цитата🎣':
        bot.send_message(message.chat.id, get_random_fishing_quote(), reply_markup=markup)

# Обработчик всех остальных текстовых сообщений
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.send_message(message.chat.id, 'Воспользуйся клавиатурой', reply_markup=markup)

# Запуск бота
keep_alive()
bot.polling()


