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

char_table= data_voice.get_table_char()
char_audio =data_voice.get_audio()

# short list for the future
characters = {'favs':['tighnari', 'zhungli', 'beidou', 'tartaglia']}
a_char = characters['favs']

@bot.message_handler(commands=['char'])
def get_char(message):

    markup = types.InlineKeyboardMarkup()
    btnlist = []
    for i in range(len(a_char)):
        markup.add(types.InlineKeyboardButton(text=a_char[i].title(), callback_data= a_char[i]))
    # второй ряд (одна кнопка)
    btn1= types.InlineKeyboardButton('geo', callback_data='d')
    btn2= types.InlineKeyboardButton('anemo', callback_data='d')
    btn3= types.InlineKeyboardButton('dendro', callback_data='d')
    btn4= types.InlineKeyboardButton('hydro', callback_data='d')
    btn5= types.InlineKeyboardButton('electro', callback_data='d')
    markup.row(btn1,btn2,btn3,btn4,btn5)
    bot.send_message(message.chat.id, text='choose day', reply_markup=markup)

def help_list(message):
    bot.send_message(message.chat.id, '<i> You can type time of the day, say hello, ask me about my friend, my troubles, what I think about us and just type chat to talk \nWe can talk about Ascension too, if you want </>', parse_mode='html') 

@bot.message_handler(commands=['farm'])
# keyboard for choosing day
def scheldule(message):
#наша клавиатура
    keyboard = types.InlineKeyboardMarkup()
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
    bot.send_message(message.chat.id, text='choose day', reply_markup=keyboard)

@bot.message_handler(commands=['lang'])
def set_lang(message):
    keyboard = types.InlineKeyboardMarkup()
    key_jp = types.InlineKeyboardButton(text='🇯🇵 japanese', callback_data='jp'); #кнопка «Да»
    keyboard.add(key_jp); 
    key_en = types.InlineKeyboardButton(text='🇬🇧 english', callback_data='en'); #кнопка «Да»
    keyboard.add(key_en); 
    bot.send_message(message.chat.id, text='💬 please choose language', reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
# getting phrases from voice data
    if message.text:
        result = data_voice.get_msg(message.text, char_table, char_audio)
        msg = result[0]
        bot.send_message(message.chat.id, '<i>'+msg+'</>', parse_mode='html')
        bot.send_audio(message.chat.id, audio=(result[1]))
    else:
        bot.send_message(message.chat.id,'Can you send me another message?')


# ------------------FARM COMMAND ---------------------------


# getting data for certain day
@bot.callback_query_handler(func=lambda call:True)
def callback_worker(call):
    global char_table
    global char_audio

    if call.data == '0':
        bot.send_message(call.message.chat.id, '*[ FARMABLE TODAY ]*', parse_mode= 'Markdownv2')
        bot.send_message(call.message.chat.id, data.get_day(0))
    elif call.data == '1':
        bot.send_message(call.message.chat.id, '*[ FARMABLE TODAY ]*', parse_mode= 'Markdownv2')
        bot.send_message(call.message.chat.id, data.get_day(1))
    elif call.data == '2':
        bot.send_message(call.message.chat.id, '*[ FARMABLE TODAY ]*', parse_mode= 'Markdownv2')
        bot.send_message(call.message.chat.id, data.get_day(2))
    elif call.data == 'jp':
        bot.send_message(call.message.chat.id, 'japan')
        char_audio =data_voice.get_audio(char, '')
    elif call.data == 'en':
        bot.send_message(call.message.chat.id, 'en')
        char_audio =data_voice.get_audio(char, '')
    elif call.data in a_char:
        for char in a_char:
            if call.data == char:
                bot.send_message(call.message.chat.id, 'Nice to meet you!')
                char_table= data_voice.get_table_char(char)
                char_audio =data_voice.get_audio(char)


bot.infinity_polling()