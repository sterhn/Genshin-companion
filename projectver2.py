import os
import telebot
import requests
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telebot import types
import data
import data_voice

# loading bot data
load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# short list for the future
char_list = ['Tighnari', 'Kokomi', 'Diona']

@bot.message_handler(commands=['help'])
def help_list(message):
    bot.send_message(message.chat.id, '<i> You can type time of the day, say hello, ask me about my friend, my troubles, what I think about us and just type chat to talk \nWe can talk about Ascension too, if you want </>', parse_mode='html') 

@bot.message_handler(commands=['farm'])
# keyboard for choosing day
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
    bot.send_message(message.chat.id, text='Choose day', reply_markup=keyboard)



@bot.message_handler(content_types=['text'])
def get_text_messages(message):
# getting phrases from voice data
    if message.text:
        result = data_voice.get_msg(message.text)
        msg = result[0]
        bot.send_message(message.chat.id, '<i>'+msg+'</>', parse_mode='html')
        bot.send_audio(message.chat.id, audio=(result[1]))
    else:
        bot.send_message(message.chat.id,'Can you send me another message?')


# ------------------FARM COMMAND ---------------------------




# getting data for certain day
@bot.callback_query_handler(func=lambda call:True)
def callback_worker(call):
    if call.data == '0':
        bot.send_message(call.message.chat.id, '*[ FARMABLE TODAY ]*', parse_mode= 'Markdownv2')
        bot.send_message(call.message.chat.id, data.get_day(0))
    elif call.data == '1':
        bot.send_message(call.message.chat.id, '*[ FARMABLE TODAY ]*', parse_mode= 'Markdownv2')
        bot.send_message(call.message.chat.id, data.get_day(1))
    elif call.data == '2':
        bot.send_message(call.message.chat.id, '*[ FARMABLE TODAY ]*', parse_mode= 'Markdownv2')
        bot.send_message(call.message.chat.id, data.get_day(2))

bot.infinity_polling()