import requests
import re
import pandas as pd
from bs4 import BeautifulSoup as bp
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv
from requests.auth import HTTPDigestAuth
load_dotenv()

# usr and pass to login (in an env file with bot token)
USER = os.environ.get('USER')
PASS = os.environ.get('PASS')



# ---------------GETTING ALL THE AUDIO FILES -------------
# get a audio file names (single url contain all links to a specific language)
url = 'https://genshin-impact.fandom.com/wiki/File:VO_JA_Tighnari_Hello.ogg'

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

# -------------GETTING SUBTITLES ---------------------
#using pandas to get all the tables
table = 'https://genshin-impact.fandom.com/wiki/Tighnari/Voice-Overs'

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

print(df)
indx = 0
text = 'When'
# audio links index corresponds to row index so you can get both link and subtitle

sub ='a'
 
# creating and passing series to new column
filt = df["Title"].apply(lambda x: text in x)
print(df['Details'].loc[df.index[filt]])
index_value = df.index[filt].to_list()
for i in index_value:
    print(links[int(i)])

def get_msg(message):
    filt = df["Title"].apply(lambda x: message.title() in x)
    msg= df['Details'].loc[df.index[filt]]
    index_value = df.index[filt].to_list()
    audio = links[index_value[0]]
    return(msg, audio)

days = ['night', 'afternoon', 'morning', 'day']
if 'morning' in days:
    print(get_msg('morning'))
else:
    print(False)