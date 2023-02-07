import os
import telebot
import requests
import re
import pandas as pd
from bs4 import BeautifulSoup as bp
from dotenv import load_dotenv
from requests.auth import HTTPDigestAuth
from telebot import types
from random import randint

# loading bot data
load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')
# usr and pass to login (in an env file with bot token)
USER = os.environ.get('USER')
PASS = os.environ.get('PASS')

bot = telebot.TeleBot(BOT_TOKEN)

# setting up a constant elements list
ELEMENTS = ['anemo', 'cryo', 'dendro', 'electro', 'geo', 'hydro', 'pyro']

# ---------------GETTING ALL THE AUDIO FILES -------------
# get a audio file names (single url contain all links to a specific language)
# depending on char name
def get_audio(character = 'Tighnari', lg = 'JA_'):
    # looking for file without any dependencies on other characters
    # low hp or similar
    url = 'https://genshin-impact.fandom.com/wiki/File:VO_'+lg+character.title()+'_Low_HP_01.ogg'
    # logging in to wiki with url
    response = requests.get(url, auth=HTTPDigestAuth(USER, PASS))
    soup = bp(response.text, 'html.parser')
    # creating a list of links
    links = []
    # regex pattern to use (probably can make it shorter but it works)
    pattern = '(https:+\/{2}\w+\.\w+\.\w+\.\w+\/.+[VO].+)'
    # getting all the links into a list
    for link in soup.find_all('a', attrs={'href': re.compile(pattern)}):
        links.append(link.get('href'))
    return links

# -------------GETTING SUBTITLES ---------------------
#using pandas to get all the tables
def get_table_char(character = 'Tighnari'):
    table = 'https://genshin-impact.fandom.com/wiki/'+character.title()+'/Voice-Overs'
    char = pd.read_html(table)
    # getting specific table with text without titles names and just audio subtitles
    df_char = char[2]
    df_char = df_char.dropna()

    # setting columns name (works better this way) 
    df = df_char.set_axis(['Title','Details'], axis=1)

    # replacing all useless text in the begining of every phrase (all of it end with ogg)
    # so using a regex again
    text = '[\s\S]*?(?:ogg)'
    df.replace(regex=True,inplace=True,to_replace=text,value=r'')
    df = df.reset_index(drop=True)
    return df


# sending a subtitle and audio message
def get_msg(message, df, links):
    emj = '💚 🦎 🦋 🐍 🌱 🌿 🍀 🍃 🌺 🌸'.split()
    emj = emj[randint(0,len(emj)-1)]
    # looking for msg in all availible voice lines
    msglist = message.title().split()
    filt = df.apply(lambda x: any([m in x[0] for m in msglist]), axis=1)
# getting text based on index of title of voice line
    msg= df['Details'].loc[df.index[filt]]
    index_value = df.index[filt].to_list()
        # if there's more than one result picking up random
    if len(index_value) >1:
        res = df[filt].sample().index
        msg= df['Details'].loc[df.index[res]] 
        return(emj + msg, links[res.to_list()[0]])
    # getting audio by index too - returning values
    audio = links[index_value[0]]
    return(emj + msg, audio)

# dict of characters with elements
def characters():
    url = 'https://genshin-impact.fandom.com/wiki/Character/List'
    char = pd.read_html(url)
    characters = {}
    t = 6
    for elem in ELEMENTS:
        characters[elem] = char[t]['Name'].to_list()
        t+=1
    return characters

# getting all 
char_audio = get_audio()
char_table = get_table_char()
chars = characters()
char = 'Tighnari'


# --------------------BOT COMMANDS -------------------
@bot.message_handler(commands=['char'])
def get_char(message):
    markup = types.InlineKeyboardMarkup()
    btns = []
    for elem in ELEMENTS:
        btn= types.InlineKeyboardButton(elem, callback_data=elem)
        btns.append(btn)
    markup.row(*btns[0:5])
    markup.row(*btns[5:7])
    bot.send_message(message.chat.id, text='choose element', reply_markup=markup)

@bot.message_handler(commands=['help'])
def help_list(message):
    bot.send_message(message.chat.id, '<i> You can type time of the day, say hello, ask me about my friend, my troubles, what I think about us and just type chat to talk \nWe can talk about Ascension too, if you want </>', parse_mode='html') 

@bot.message_handler(commands=['lang'])
def set_lang(message):
    keyboard = types.InlineKeyboardMarkup()
    key_jp = types.InlineKeyboardButton(text='🇯🇵 japanese', callback_data='jp'); #кнопка «Да»
    keyboard.add(key_jp); 
    key_en = types.InlineKeyboardButton(text='🇬🇧 english', callback_data='en'); #кнопка «Да»
    keyboard.add(key_en); 
    bot.send_message(message.chat.id, text='💬 please choose language', reply_markup=keyboard)


# -------------------BOT CHATTING----------------
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
# getting phrases from voice data
    if message.text:
        result = get_msg(message.text, char_table, char_audio)
        msg = result[0]
        bot.send_message(message.chat.id, '<i>'+msg+'</>', parse_mode='html')
        bot.send_audio(message.chat.id, audio=(result[1]))



@bot.callback_query_handler(func=lambda call:True)
def callback_worker(call):
    global char_audio
    global char_table
    global char
    # setting language and changing auidio links to set language
    if call.data == 'jp':
        bot.send_message(call.message.chat.id, 'Okay, I\'m gonna talk with you in Japanese!')
        char_audio = get_audio(char, 'JA_')
    elif call.data == 'en':
        bot.send_message(call.message.chat.id, 'Okay, I\'m gonna talk with you in English!')
        char_audio = get_audio(char, '')

# shows buttons with characters in two columns, set callback to char name
    elif call.data in ELEMENTS:
        markup = types.InlineKeyboardMarkup()
        btns = []
        for char in chars[call.data]:
            btn= types.InlineKeyboardButton(char, callback_data=char)
            btns.append(btn)
        for i in range(0, len(btns), 2):
            try:
                markup.row(btns[i], btns[i+1])
            except:
                markup.add(btns[i])
        bot.send_message(call.message.chat.id, text='choose character', reply_markup=markup)
    
    elif any(call.data in val for val in chars.values()):
        char=call.data.replace(' ', '_')
        char_table = get_table_char(char)
        char_audio = get_audio(char)
        bot.send_message(call.message.chat.id, f'Nice to meet you, I\'m {call.data}')


bot.infinity_polling()
if __name__ == '__main__':
    projectver3.run()