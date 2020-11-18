# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 07:24:14 2020

@author: tommy
"""

import json
import matplotlib.pyplot as plt
import re
from collections import defaultdict
plt.style.use('ggplot')

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

# plot chart of most frequently posting users
freq = defaultdict(int)
for message in messages:
    freq[message['author']['name']] += 1

sorted_freq = [(k, v) for k, v in sorted(freq.items(), key=lambda item: item[1]) if v > 50]

plt.figure(num=None, figsize=(9, 4), dpi=80, facecolor='w', edgecolor='k')
plt.bar(*zip(*sorted_freq))
plt.xlabel('User')
plt.ylabel('Messages')
plt.title('Amount of Intellectual Thought Generated per User')
plt.xticks(rotation=75)
plt.show()
#plt.savefig('flat_earth_plot.png', bbox_inches='tight')