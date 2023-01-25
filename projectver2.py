import os
import telebot
import requests
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telebot import types
import data
import data_voice
load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)




@bot.message_handler(commands=['farm'])
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

@bot.message_handler(commands=['help'])
def help_list(message):
    bot.send_message(message.chat.id, 'WIP') 

@bot.message_handler(commands=['audio'])
def audio(message):
    bot.send_message(message.chat.id, 'Hello, I\'m Tighnari, Forest Watcher affiliated with the Avidya Forest. My work is to keep the rainforest\'s ecosystem and those who enter the forest safe. If you\'re a newcomer, I suggest reading the "Avidya Forest Survival Guide", especially the section "How to distinguish between edible and poison mushrooms')
    bot.send_audio(message.chat.id, audio=('https://static.wikia.nocookie.net/gensin-impact/images/6/6b/VO_JA_Tighnari_Hello.ogg/revision/latest?cb=20220828121304')) 

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    days = ['night', 'afternoon','evening', 'morning', 'day', 'birthday', 'hobbies', 'troubles']
    if message.text.lower() in days:
        result = data_voice.get_msg(message.text)
        bot.send_message(message.chat.id,result[0])
        bot.send_audio(message.chat.id, audio=(result[1]))
    else:
        bot.send_message(message.chat.id,'Can you send me another message?')




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