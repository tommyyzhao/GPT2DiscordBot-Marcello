# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 07:24:14 2020

@author: tommy zhao

Basic data cleaning for Discord Data
"""

import math
import json
import re
import random


def reduce_duplicates(msg, min_repeats = 4): 
    ''' 
    overengineered method to reduce duplicate chars in string to
    a maximum of min_repeats + the sqrt of trailing chars after min_repeats
    '''
    
    new_string = ''
    
    prev_char = ''
    dup_count = 0
    for char in msg:
        if char != prev_char:
            if dup_count > 0:
                if dup_count > min_repeats:
                    for _ in range(int(math.sqrt(dup_count-min_repeats)) + min_repeats):
                        new_string = new_string + prev_char
                else:
                    for _ in range(dup_count):
                        new_string = new_string + prev_char
            prev_char = char
            dup_count = 0
            new_string = new_string + char
        else:
            dup_count += 1
            
    if dup_count > 0:
        if dup_count > min_repeats:
            for _ in range(int(math.sqrt(dup_count-min_repeats)) + min_repeats):
                new_string = new_string + prev_char
        else:
            for _ in range(dup_count):
                new_string = new_string + prev_char
            
    return new_string 


files = ['flat-earth-discussions.json', 'saturday-nights-with-the-boys.json', 
         'intellectual-thought.json', 'dm-8-group.json', 'dm-7-group.json', 'dm - crmbob5.json']
random.shuffle(files)
messages = []
for file in files:
    with open(f"./raw/{file}") as f:
         data = json.load(f)
    # get message log
    messages = messages + data['messages']

# get set of users
users = set([(msg['author']['id'], msg['author']['name']) for msg in messages])


prev_author = '' #keep track of prev author
prev_content = '' #track previous content to avoid repeats
text = ''
for msg in messages:
    # load content and author
    content = msg['content']
    author = msg['author']['name']
    # skip bots
    if author == 'Dyno' or author == 'Candy Music': continue
    
    #remove links
    content = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', content)
    # reduce duplicate chars
    content = reduce_duplicates(content, min_repeats=3)
        
    #strip whitespace
    content = content.strip()
    #skip empty messages
    if not content: continue
    
    #skip messages that are only contain mentions
    if re.sub("(@[A-Za-z0-9_]+)","", content).strip() == "": continue
    #skip messages that only contain numbers and/or periods
    if not re.compile(r'[^0-9.^k]').search(content): continue
    #skip messages that end in .net or .com
    if content.endswith('.net') or content.endswith('.com'): continue
    #remove end noise
    if content.endswith(']') or content.endswith('\\'): 
        content = content[:-1]
    #get rid of bot commands
    if content.startswith('/') or content.startswith('-') or content.startswith('.')\
        or content.startswith('Started a call') or content.startswith('Added a recipient')\
        or content.startswith('Removed a recipient') or content.startswith('cmp')\
        or content.startswith('cms') or content.startswith('@Dyno'): continue
    #skip join messages and 'Pinned a message' messages
    if content == 'Joined the server.' or content == 'Pinned a message.' or \
        content == 'join':
        continue
    
    #skip duplicate messages from the same author
    if content == prev_content and author == prev_author: continue
    
    prev_content = content
    
    # if the author is the same as before, don't add an <|end|> token
    if author == prev_author:
        text = text + '\n' + msg['content'] + '\n'
    else:
        text = text + f"\n<{author}>\n{content}"
        prev_author = author
    
with open('original_flatearth_shuffled2.txt', 'w', encoding = 'utf-8') as f:
    f.write(text)
