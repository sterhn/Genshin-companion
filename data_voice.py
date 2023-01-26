import requests
import re
import pandas as pd
import os
from random import randint
from bs4 import BeautifulSoup as bp
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from requests.auth import HTTPDigestAuth

load_dotenv()

# usr and pass to login (in an env file with bot token)
USER = os.environ.get('USER')
PASS = os.environ.get('PASS')

# ---------------GETTING CHARACTER----------------
# will update later


# ---------------GETTING ALL THE AUDIO FILES -------------
# get a audio file names (single url contain all links to a specific language)
# depending on char name
def get_audio(character = 'Tighnari', lg = '_JA_'):
    url = 'https://genshin-impact.fandom.com/wiki/File:VO' +lg+character.title()+'_Hello.ogg'
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

emoj_list = ('💚 🦎 🦋 🐍 🌱 🌿 🍀 🍃 🌺 🌸').split()



def get_msg(message, df, links):
    emj = emoj_list[randint(0,len(emoj_list)-1)]
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





    

