# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 07:24:14 2020

@author: tommy zhao

Basic data cleaning for Discord Data
"""

import json
import random
import re



# convert list of synonyms to usable dictionary
synonyms = {}
for synonym_set in synonym_set_list:
    for synonym in synonym_set:
        synonyms[synonym] = synonym_set.difference({synonym})


# read original data
lines = []
with open('original_flatearth.txt', 'r', encoding = 'utf-8') as f:
    for line in f:
        lines.append(line)
        
# regex to recognize user tags
user_match = re.compile(r'^<[A-Za-z0-9]+>$')
with open('augmented3.txt', 'w', encoding = 'utf-8') as f:
    for line in lines:
        if user_match.match(line.strip()):
            f.write(line)
        else:
            tokens = line.split()
            new_tokens = []
            for token in tokens:
                # replace word with its synonym 80% of the time, if it has a synonym
                if token.lower() in synonyms and random.random() > 0.2:
                    synonym = random.sample(synonyms[token.lower()], 1)[0]
                    # try to preserve capitalization
                    if token.isupper():
                        synonym = synonym.upper()
                    elif token[0].isupper:
                        synonym = synonym[0].upper() + synonym[0:]
                    new_tokens.append(random.sample(synonyms[token.lower()], 1)[0])
                else:
                    new_tokens.append(token)
            new_tokens.append('\n')
            new_line = ' '.join(new_tokens)
            f.write(new_line)
 
# list of sets of relevant synonyms for the flat-earth discord
synonym_set_list = [
    {'bolaji', 'mobologo', 'bobol', 'bobo', 'bolagi', 'bolag', 'bolaj', 'mobo', 'boboli'},
    {'caleb', 'clb', 'Caleb', 'kalub', 'clabu', 'kaleb', 'pandoge'},
    {'derek', 'drk', 'derick', 'Derek'},
    {'benji', 'adam', 'Adam', 'Benji'},
    {'colin', 'conor', 'connor'},
    {'eimer', 'elmer'},
    {'mate', 'm8'},
    {'bruh', 'bro', 'bruv'},
    {'pls', 'plz', 'please'},
    {'yeah', 'yea', 'yep', 'yup', 'ye'},
    {'boy', 'boi'},
    {'babe', 'bb', 'BB'},
    {'wut', 'wat'},
    {'you', 'u'},
    {'no', 'nah', 'nope'},
    {'sucks', 'sux'},
    {'love', 'lov', 'luv'},
    {'true', 'tru'},
    {'im', "i'm", "I'm", "Im"},
    {'hows', "how's"},
    {'i', "I"},
    {'idk', "idek"},
    {'with', "w"},
    {'ima', "imma"},
    {'lol', "haha", 'lmao'},
    {'whos', "who's"},
    {'because', "cause", "cuz"},
    {'ight', "aight", "alright"},
    {'tho', "though"},
    {'dont', "don't"},
    {'youre', 'ur', "you're"},
    {'yours', 'urs'},
    ]