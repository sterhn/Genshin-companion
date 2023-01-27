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
char = 'Tighnari'

# getticnh talents farming scheldule as a dictionary
def scheldule_data():
    # getting data
    page = requests.get("https://paimon.moe/items")
    # data but prettier
    data = bp(page.content, 'html.parser')
    # all talents and characters 
    talents= data.find('table', class_='w-full block p-4 bg-item rounded-xl')
    chars = data.find_all('td', class_ = 'border-gray-700 border-b py-2 svelte-xhx6q1')
    # patterns for talents and names
    pattern_t = '\<\w*\>(\w+\ *)\<\w*'
    pattern_n = '([A-Z][a-z]*\s*\(*\w+\)*)'
    # formating talents names and getting it into a list
    r_talents = re.compile(pattern_t).findall(str(talents))
    # days for dictionary
    days = ['Monday/Thursday', 'Tuesday/Friday', 'Wednesday/Saturday']
    # empty dict with future scheldule
    scheldule = {}
    # empty char list corresponding to talents
    char_list = []
    # talents ad days counter
    t, day  = 0, 0
    # emojis to make it prettier
    emoj_list = ['🧡','💛','💚','💙','💜','🖤','🤍']
    # lookinf for all lines of characters
    for i in range(len(chars)):
        # formatted chars names in a list
        char = re.compile(pattern_n).findall(str(chars[i]))
        # joining it all in a pretty string
        char_str = ', '.join(char)
        # if line not empty
        if char !=[]:
            # formatting result string in 'talents:list of chars'
            emj =emoj_list[randint(0,len(emoj_list)-1)] 
            res = str(f'{emj} {r_talents[t]}: {char_str} \n')
            char_list.append(res)
            # moving to next talent
            t+=1
        # if line is empty moving to next day
        else:
            # adding previous char and talents 
            scheldule[days[day]]=char_list
            # clearing list
            char_list = []
            day+=1
    return scheldule

# function for getting result
def get_day(day):
    return '\n'.join(list(scheldule_data().values())[day])

# ---------------CHARACTERS CHATS -----------------------


# ---------------GETTING ALL THE AUDIO FILES -------------
# get a audio file names (single url contain all links to a specific language)
# depending on char name
def get_audio(character = 'Tighnari', lg = 'JA_'):
    url = 'https://genshin-impact.fandom.com/wiki/File:VO_' +lg+character.title()+'_Hello.ogg'
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

    # setting a single column name (works better this way) 
    df = df_char.set_axis(['Title','Details'], axis=1)

    # replacing all useless text in the begining of every phrase (all of it end with ogg)
    # so using a regex again
    text = '[\s\S]*?(?:ogg)'
    df.replace(regex=True,inplace=True,to_replace=text,value=r'')
    df = df.reset_index(drop=True)
    return df



def get_msg(message, df, links):
    emj = '💚 🦎 🦋 🐍 🌱 🌿 🍀 🍃 🌺 🌸'.split()
    emj = emj[randint(0,len(emj)-1)]
    filt = df["Title"].apply(lambda x: message.title() in x)
    if not any(filt):
        text ='Sorry, I don\'t understand you. Can you ask me about something else? \n'
        filt = df["Title"].apply(lambda x: 'Mistakes' in x)
        msg= df['Details'].loc[df.index[filt]]
        index_value = df.index[filt].to_list()
        audio = links[index_value[0]]
        return(text + msg, audio)
    else:
        msg= df['Details'].loc[df.index[filt]]
        index_value = df.index[filt].to_list()
        if len(index_value) >1:
            res = df[filt].sample().index
            msg= df['Details'].loc[df.index[res]] 
            return(emj + msg, links[res.to_list()[0]])
        
        audio = links[index_value[0]]
        return(emj + msg, audio)

char_audio = get_audio()
char_table = get_table_char()

# short list for the future
characters = {'favs':['tighnari', 'zhongli', 'beidou', 'tartaglia']}
a_char = characters['favs']
# --------------------BOT COMMANDS -------------------
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

@bot.message_handler(commands=['help'])
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


# -------------------BOT CHATTING----------------
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
# getting phrases from voice data
    if message.text:
        result = get_msg(message.text, char_table, char_audio)
        msg = result[0]
        bot.send_message(message.chat.id, '<i>'+msg+'</>', parse_mode='html')
        bot.send_audio(message.chat.id, audio=(result[1]))
    else:
        bot.send_message(message.chat.id,'Can you send me another message?')


# ------------------FARM COMMAND ---------------------------
# getting data for certain day
@bot.callback_query_handler(func=lambda call:True)
def callback_worker(call):
    global char_audio
    global char_table
    global char
    if call.data == '0':
        bot.send_message(call.message.chat.id, '*[ FARMABLE TODAY ]*', parse_mode= 'Markdownv2')
        bot.send_message(call.message.chat.id, get_day(0))
    elif call.data == '1':
        bot.send_message(call.message.chat.id, '*[ FARMABLE TODAY ]*', parse_mode= 'Markdownv2')
        bot.send_message(call.message.chat.id, get_day(1))
    elif call.data == '2':
        bot.send_message(call.message.chat.id, '*[ FARMABLE TODAY ]*', parse_mode= 'Markdownv2')
        bot.send_message(call.message.chat.id, get_day(2))

    elif call.data == 'jp':
        bot.send_message(call.message.chat.id, 'Okay, I\'m gonna talk with you in Japanese!')
        char_audio = get_audio(char)
    elif call.data == 'en':
        bot.send_message(call.message.chat.id, 'Okay, I\'m gonna talk with you in English!')
        char_audio = get_audio(char, '')
    elif call.data in a_char:
        for chars in a_char:
            if call.data == chars:
                char = chars
                bot.send_message(call.message.chat.id, 'Nice to meet you!')
                char_table= get_table_char(char)
                char_audio = get_audio(char)


bot.infinity_polling()