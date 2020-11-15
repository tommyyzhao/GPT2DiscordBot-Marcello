# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 07:24:14 2020

@author: tommy zhao

Basic data cleaning for Discord Data
"""

import json
import re
from collections import defaultdict

files = ['flat-earth-discussions.json', 'saturday-nights-with-the-boys.json', 
         'intellectual-thought.json']

messages = []
for file in files:
    with open(file) as f:
         data = json.load(f)
    # get message log
    messages = messages + data['messages']

# get set of users
users = set([(msg['author']['id'], msg['author']['name']) for msg in messages])


prev_author = '' #keep track of prev author
prev_content = '' #track previous content to avoid repeats
text = ''
for msg in messages:
    author = msg['author']['name']
    content = msg['content']
    
    #remove links
    content = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', content)
    #strip whitespace
    content = content.strip()
    #skip empty messages
    if not content: continue
    
    #skip messages that are only contain mentions
    if re.sub("(@[A-Za-z0-9_]+)","", content).strip() == "": continue
    #skip messages that only contain numbers and/or periods
    if not re.compile(r'[^0-9.^]').search(content): continue
    #skip messages that end in .net or .com
    if content.endswith('.net') or content.endswith('.com'): continue
    #get rid of bot commands
    if content.startswith('/') or content.startswith('-'): continue
    #skip 'Joined the server' and 'Pinned a message' messages
    if content == 'Joined the server.' or content == 'Pinned a message.':
        continue
    
    #skip duplicate messages from the same author
    if content == prev_content and author == prev_author: continue
    
    prev_content = content
    
    # if the author is the same as before, don't add an <|end|> token
    if author == prev_author:
        text = text + msg['content'] + ' \n '
    else:
        prev_author = author
        text = text + f"<|end|> \n {author}: \n {content} \n "
    
with open('output_data.txt', 'w', encoding = 'utf-8') as f:
    f.write(text)
