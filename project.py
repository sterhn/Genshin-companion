import os
import telebot
import requests
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telebot import types
import data
load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == ('Привет' or 'привет'):
        bot.send_message(message.chat.id, 'Привет, напиши /start чтобы начать и /help для помощи')
    elif message.text == ('Hello' or 'hello'):
        bot.send_message(message.chat.id, 'Hi! type /start to start or /help for commands list')
    elif message.text == '/help':
        bot.send_message(message.chat.id, 'WIP') 
    elif message.text == '/start':
        scheldule(message)
    else:
        bot.send_message(message.chat.id, 'Type /start to start or /help for commands list')

@bot.message_handler(commands=['start'])
def scheldule(message):
    keyboard = types.InlineKeyboardMarkup(); #наша клавиатура
    key_m = types.InlineKeyboardButton(text='Monday', callback_data='0'); #кнопка «Да»
    keyboard.add(key_m); 
    key_t = types.InlineKeyboardButton(text='Tuesday', callback_data='1'); #кнопка «Да»
    keyboard.add(key_t); 
    key_w= types.InlineKeyboardButton(text='Wednesday', callback_data='2');
    keyboard.add(key_w);
    key_th= types.InlineKeyboardButton(text='Thursday', callback_data='0');
    keyboard.add(key_th);
    key_f= types.InlineKeyboardButton(text='Friday', callback_data='1');
    keyboard.add(key_f);
    key_sat= types.InlineKeyboardButton(text='Saturday', callback_data='2');
    keyboard.add(key_sat);
    key_sun= types.InlineKeyboardButton(text='Sunday', callback_data='sun');
    keyboard.add(key_sun);
    bot.send_message(message.chat.id, text='Choose day', reply_markup=keyboard)



@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    msg = '[farmable today]'
    if call.data == '0': #call.data это callback_data, которую мы указали при объявлении кнопки
        bot.send_message(call.message.chat.id, msg)
        bot.send_message(call.message.chat.id, data.get_day(0))
    elif call.data == '1':
        bot.send_message(call.message.chat.id, msg)
        bot.send_message(call.message.chat.id, data.get_day(1))
    elif call.data == '2':
        bot.send_message(call.message.chat.id, msg)
        bot.send_message(call.message.chat.id, data.get_day(2))
    elif call.data == 'sun':
        bot.send_message(call.message.chat.id, msg)
        for i in range(3):
            bot.send_message(call.message.chat.id, data.get_day(i))
    



bot.infinity_polling()