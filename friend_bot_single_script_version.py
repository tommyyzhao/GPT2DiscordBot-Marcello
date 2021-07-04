import gpt_2_simple as gpt2
import discord
from discord.ext import commands
from discord.utils import get
import random
import time
import re
import os

CHECKPOINT_MODEL ='run_flat_earth_355M_v2.2'
sess = gpt2.start_tf_sess()
gpt2.load_gpt2(sess, run_name=CHECKPOINT_MODEL)

# Defining constants
TEST_CHANNEL = 776592860723937301
SECRET_TEST_CHANNEL = 507560608430817290
FES_CHANNEL = 416242332241887244
CHECKPOINT_MODEL ='run_flat_earth_355M_v2.2'
MAIN_USERS = ['Wanderer', 'Pandoge', 'blownking', 'crmbob5', 'Fl3tchr', 'mrbabybob', 'BenjiMcmuscles', 'ztoms', 'mynameismili']

# GPT2 Bot settings
is_inferencing = False #boolean to check if bot is busy
use_history = True
use_bot_in_history = False
user_aware = True

BOT_LINE_LIMIT = 8
reply_chance = 0.1
temperature = 0.73
character_limit = 75
lookback_length = 15

client = commands.Bot(command_prefix = '.', allowed_mentions=discord.AllowedMentions.none())

# -------------------- Discord Commands -------------------- #
@client.event
async def on_ready():
    global secret_channel, fes_channel, simulator_channel
    simulator_channel = client.get_channel(TEST_CHANNEL)
    secret_channel = client.get_channel(SECRET_TEST_CHANNEL)
    fes_channel = client.get_channel(FES_CHANNEL)
    
    await secret_channel.send("Connected")
    print('Bot is online')

@client.event
async def on_message(message):
    print(f"received a message: {message.content}")
    random.seed()
    if message.content and not message.content.startswith('.') and not message.content.startswith('http')  \
                and random.random() < reply_chance and not str(message.author).startswith('Intellectual'):
        print('RANDOM RESPONSE TRIGGERED')
        await randomMessageReply(message)
    else:
      await client.process_commands(message)


@client.command()
@commands.is_owner()
async def debugM(ctx, *, msg):
    await secret_channel.send(msg)

@client.command()
@commands.is_owner()
async def setM(ctx, *, msg):
    await fes_channel.send(msg)

@client.command(brief='values between [0-1]. lower temp means less crazy text.')
async def setTemp(ctx, temp):
    global temperature
    try:
        t = min(float(temp), 1)
    except:
        await ctx.send("invalid temperature")
    temperature = t
    await ctx.send(f"Changed GPT2 temperature setting to {t}.")

@client.command(brief='set chance for random response to a message.')
async def setReplyChance(ctx, chance):
    global reply_chance
    try:
        new_chance = min(float(chance), 1)
    except:
        await ctx.send("invalid input")
    reply_chance = new_chance
    await ctx.send(f"Changed reply chance to {new_chance}.")
    
@client.command(brief='set character_limit for bot responses')
async def setCharLimit(ctx, lim):
    global character_limit
    try:
        new_lim = int(lim)
    except:
        await ctx.send("invalid input")
    character_limit = new_lim
    await ctx.send(f"Changed character limit to {new_lim}.")

@client.command(brief='how far the bot looks back into the history')
async def setLookbackLimit(ctx, lim):
    global lookback_length
    try:
        lookback_length = int(lim)
    except:
        await ctx.send("invalid input")
    lookback_length = lim
    await ctx.send(f"Changed character limit to {lim}.")

@client.command()
@commands.is_owner()
async def shutdown(ctx):
    print('shutdown command received')
    await ctx.send("Shutting down.")
    await ctx.bot.logout()

@client.command(brief='toggles usage of chat history when generating responses')
async def useHistory(ctx):
    global use_history
    use_history = not use_history
    print(await get_historical_prompt(ctx))
    await ctx.send(f"Using message history: {use_history}")

@client.command(brief='whether bot generated responses are incorporated into history')
async def useBotInHistory(ctx):
    global use_bot_in_history
    use_bot_in_history = not use_bot_in_history
    await ctx.send(f"Using bot in history: {use_bot_in_history}")

@client.command(brief='whether the user sending the command is considered')
async def userAware(ctx):
    global user_aware
    user_aware = not user_aware
    await ctx.send(f"User aware: {user_aware}")

@client.command(brief='list of current settings and their values')
async def settings(ctx):
    await ctx.send(f'''
    Current settings:
    User aware: {user_aware}
    Using chat history: {use_history}
    Using bot responses as history: {use_bot_in_history}
    Temperature: {temperature}
    Reply chance: {reply_chance}
    Bot line limit: {BOT_LINE_LIMIT}
    Bot char limit: {BOT_LINE_LIMIT}
    ''')
# --------------------- GPT-2 Methods ------------------------ #

# the main GPT-2 inference method
async def inference(prompt, length=100, nsamples=4):
    start = time.time()        
    
    texts = gpt2.generate(sess,
        run_name=CHECKPOINT_MODEL,
        length=character_limit,
        temperature=temperature,
        top_p=0.9,
        prefix=prompt,
        return_as_list=True,
        nsamples=nsamples,
        batch_size=nsamples
        )
    print(f'\nINFERENCING {len(texts)} samples took {round(time.time() - start, 2)} seconds\n')
    
    return texts

# method to allow text filtering functionality -- for now just filtering one-word responses
def filter_texts(texts, split):
    filtered_responses = []
    unfiltered_responses = []
    
    for i, text in enumerate(texts):
        # clean generated text
        clean_text = ''.join(text.split(split)[1:]) # split by user_name 
        clean_text = re.sub(' +', ' ', clean_text) #remove multiple spaces
        print(f'\nNON-TRUNCATED RESPONSE {i}:\n{clean_text}\n')
        
        # truncate at next user
        try:
            truncate_at = re.search('<[A-Za-z0-9 ]+>', clean_text).start() #find the next user's string
            clean_text = clean_text[:truncate_at].strip()
            print(f'\nCLEANED RESPONSE {i}:\n{clean_text}')
            if not clean_text:
                print(f'\nCLEANED RESPONSE {i} is empty, skipping')
                continue
        except:
            print(f'ERROR truncating cleaned text:\n{clean_text}')
            continue
        
        unfiltered_responses.append(clean_text)
        # check for one word responses
        if len(clean_text.split()) <= 1:
            # discourage one word responses
            allowed = ['no', 'yes', 'sure']
            if clean_text.split()[0] not in allowed and random.random() > 0.25:
                print(f'Response {i}: {clean_text} is less than a word long, filtering')
                continue
        else:
            filtered_responses.append(clean_text)
            
    return filtered_responses if filtered_responses else unfiltered_responses

# get chat history on discord, format in the same format I used for training
async def get_historical_prompt(ctx, nmessages = 10):
    prior_messages = []
    async for msg in ctx.channel.history(limit=lookback_length):
        prior_messages.append(msg)
    prior_messages.reverse() #reverse messages to build the prompt chronologically
    
    history_prompt = ''
    prev_author = ''
    for msg in prior_messages:
        text = msg.content
        author_name = str(msg.author)
        author_name = author_name[:author_name.index('#')]
        
        # process bot messages
        simulated = False
        if author_name == "Intellectual Thought Generator":
            if not use_bot_in_history:
                continue
            for line in text.split('\n'):
                if line.endswith('Bot says..'):
                    simulated = True
                    simulated_user = line.replace('Bot says..', '').strip()
                    prev_author = simulated_user
                    history_prompt = history_prompt + f'<{simulated_user}>\n'
                elif simulated:
                    history_prompt = history_prompt + f'{line}\n'
            continue
        
        # clean bot commands from message content
        if '.bot' in text:
            text = re.sub(r'^\.bot', '', text).strip()
        else:
            text = re.sub(r'^\.[A-Za-z]+', '', text).strip()
            
        # fix role mentions
        if '<@&' in text:
            corrected = []
            for substr in text.split('<@&'):
                mention = re.compile(r'^!?([0-9]+)>')
                match = mention.match(substr)
                if match:
                    trim = match.span()[1]
                    roleid = int(match.group(1))
                    role = get(msg.guild.roles, id=roleid)
                    corrected_string = '@' + str(role.name) + substr[trim:]
                    corrected.append(corrected_string)
                else:
                    corrected.append(substr)
            text = ''.join(corrected)
        
        # fix mentions
        if '<@' in text:
            corrected = []
            for substr in text.split('<@'):
                mention = re.compile(r'^!?([0-9]+)>')
                match = mention.match(substr)
                if match:
                    trim = match.span()[1]
                    userid = match.group(1)
                    user = await client.fetch_user(userid)
                    corrected_string = '@' + str(user.name) + substr[trim:]
                    corrected.append(corrected_string)
                else:
                    corrected.append(substr)
            text = ''.join(corrected)
            
        
            
        # skip empty messages
        if not text:
            continue 
        
        if author_name != prev_author:
            history_prompt = history_prompt + f'<{author_name}>\n{text}\n'
            prev_author = author_name
        else:
            history_prompt = history_prompt + f'{text}\n'
        
    return history_prompt

# prompt GPT2 with a given user and message, GPT2 will respond as that user
@client.command(brief= ".bot <username> <message> to talk to <username>'s bot")
async def bot(ctx, user_name, *, prompt):
  print(f'\nbot command received message: {ctx.message.content} from channel: {ctx.message.channel}')
  global is_inferencing
  if is_inferencing:
      print('already inferencing, cant respond')
      await ctx.send("Could not respond, already responding")
      return
  # get user who sent the message
  other_user = str(ctx.message.author)
  other_user = other_user[:other_user.index('#')]

  if use_history:
      # setup historical prompt
      history_prompt = await get_historical_prompt(ctx.message, nmessages=12)
      augmented_prompt = history_prompt + f'<{user_name}>'
  else:
      if user_aware:
        augmented_prompt = f'<{other_user}>\n{prompt}\n<{user_name}>\n'
      else:
        augmented_prompt = f'{prompt}\n<{user_name}>\n'
      
  async with ctx.typing():
      is_inferencing = True
      print(f'Augmented prompt to be:\n{augmented_prompt}')
      texts = await inference(augmented_prompt, length=50)
      is_inferencing = False
      
  filtered_responses = filter_texts(texts, augmented_prompt)
  # process text
  response = random.sample(filtered_responses, 1)[0]
  lines = response.split('\n') #split on newline and limit num of lines in response
  intro_line = f'{user_name} Bot says..'
  lines = [intro_line] + lines
  response = '\n'.join(lines[:BOT_LINE_LIMIT]) #limit # lines
  print(f'Output response:\n{response}')
  await ctx.send(response)

# method for the bot to act like the user just asked a Discord server in a parallel (GPT2) universe
@client.command(brief=".askthemultiverse <message> to send a message to the multiverse")
async def askthemultiverse(ctx, *, prompt):
    global is_inferencing
    if is_inferencing:
        await ctx.send("Could not respond, already responding")
        return
    
    print(f'\nMULTIVERSE command received message: {ctx.message.content} from channel: {ctx.message.channel}')
    
    other_user = str(ctx.message.author)
    other_user = other_user[:other_user.index('#')]
    random_user = random.sample(MAIN_USERS, 1)[0]
    split_prompt = '' # prompt to split the generated response on
    
    if use_history:
        # setup historical prompt
        history_prompt = await get_historical_prompt(ctx.message, nmessages=15)
        augmented_prompt = history_prompt + f'<{random_user}>'
        split_prompt = history_prompt
    else:
        if user_aware:
            augmented_prompt = f'<{other_user}>\n{prompt}\n<{random_user}>\n'
            split_prompt = f'<{other_user}>\n{prompt}\n'
        else:
            augmented_prompt = f'{prompt}\n<{random_user}>\n'
            split_prompt = f'{prompt}\n'
    
    print(f'\nAugmented prompt to be:\n{augmented_prompt}')
        
    async with ctx.typing():
        is_inferencing = True
        texts = await inference(augmented_prompt, length=68, nsamples=1)
        
    # process text
    response = texts[0]
    print(f'\nResponse:\n{response}')
    
    clean_text = ''.join(response.split(split_prompt)[1:]) # split using split prompt
    clean_text = re.sub(' +', ' ', clean_text) #remove multiple spaces
    
    lines = clean_text.split('\n') #split on newline
    
    prev_reply = ''
    reply = ''
    current_user = ''
    repetition_counter = 1
    
    #30 lines of code just so it responds message by message
    first_response = True # no delay for first response
    for line in lines:
        user_match = re.match('<([A-Za-z0-9 ]+)>', line)
        
        if user_match:
            if first_response:
                first_response = False
            else:
                async with ctx.typing():
                    time.sleep((random.random()*5) + 1)
            current_user = user_match.group(1)
            # send previous user's reply on new user
            if reply:
                await ctx.send(reply)
                reply = ''
                # add typing indicator between pauses
                time.sleep((random.random()*3) + 1)
            reply = reply + f'{current_user} Bot says..'
        else:
            if not current_user:
                print('error finding first user')
                continue
            # skip incomplete line (usually at the end of generated response)
            if line.startswith('<'): 
                print('skipping incomplete line')
                continue
            else:
                if line == prev_reply:
                    print('repetition detected')
                    repetition_counter += 1
                    if repetition_counter > 2:
                        await ctx.send('Repetition detected, terminating.')
                        break
                else:
                    prev_reply = line
                reply = reply + '\n' + line
    if reply and not reply.endswith('Bot says..'):
        await ctx.send(reply)
            
    is_inferencing = False
    
# give GPT-2 any prompt
@client.command(brief=".askmarcello <message> to ask the bot")
async def askmarcello(ctx, *, prompt):
    global is_inferencing
    if is_inferencing:
        await ctx.send("Could not respond, already responding")
        return
    
    print(f'\nMULTIVERSE command received message: {ctx.message.content} from channel: {ctx.message.channel}')
    
    other_user = str(ctx.message.author)
    other_user = other_user[:other_user.index('#')]
    split_prompt = '' # prompt to split the generated response on
    
    augmented_prompt = f'{prompt}\n<marcello>\n'
    split_prompt = f'{prompt}\n'
    
    print(f'\nAugmented prompt to be:\n{augmented_prompt}')
        
    async with ctx.typing():
        is_inferencing = True
        texts = await inference(augmented_prompt, length=68, nsamples=1)
        
    # process text
    response = texts[0]
    print(f'\nResponse:\n{response}')
    
    clean_text = ''.join(response.split(split_prompt)[1:]) # split using split prompt
    clean_text = re.sub(' +', ' ', clean_text) #remove multiple spaces
    
    lines = clean_text.split('\n') #split on newline
    
    prev_reply = ''
    reply = ''
    current_user = ''
    repetition_counter = 1
    
    #30 lines of code just so it responds message by message
    first_response = True # no delay for first response
    for line in lines:
        user_match = re.match('<([A-Za-z0-9 ]+)>', line)
        
        if user_match:
            if first_response:
                first_response = False
            else:
                async with ctx.typing():
                    time.sleep((random.random()*5) + 1)
            current_user = user_match.group(1)
            # send previous user's reply on new user
            if reply:
                await ctx.send(reply)
                reply = ''
                # add typing indicator between pauses
                time.sleep((random.random()*3) + 1)
            if current_user == 'marcello':
                reply = reply + f'{current_user} says..'
            else:
                reply = reply + f'{current_user} Bot says..'
        else:
            if not current_user:
                print('error finding first user')
                continue
            # skip incomplete line (usually at the end of generated response)
            if line.startswith('<'): 
                print('skipping incomplete line')
                continue
            else:
                if line == prev_reply:
                    print('repetition detected')
                    repetition_counter += 1
                    if repetition_counter > 2:
                        await ctx.send('Repetition detected, terminating.')
                        break
                else:
                    prev_reply = line
                reply = reply + '\n' + line
    if reply and not reply.endswith('says..'):
        await ctx.send(reply)
            
    is_inferencing = False
    
# ask GPT-2 with a given user as the responder
@client.command(brief=".multiversewithuser <user> <message> get a user to respond in the multiverse")
async def multiversewithuser(ctx, user_name, *, prompt):
    global is_inferencing
    if is_inferencing:
        await ctx.send("Could not respond, already responding")
        return
    
    print(f'\nMULTIVERSE command received message: {ctx.message.content} from channel: {ctx.message.channel}')
    
    other_user = str(ctx.message.author)
    other_user = other_user[:other_user.index('#')]
    random_user = user_name
    split_prompt = '' # prompt to split the generated response on
    
    if use_history:
        # setup historical prompt
        history_prompt = await get_historical_prompt(ctx.message, nmessages=15)
        augmented_prompt = history_prompt + f'<{random_user}>'
        split_prompt = history_prompt
    else:
        if user_aware:
            augmented_prompt = f'<{other_user}>\n{prompt}\n<{random_user}>\n'
            split_prompt = f'<{other_user}>\n{prompt}\n'
        else:
            augmented_prompt = f'{prompt}\n<{random_user}>\n'
            split_prompt = f'{prompt}\n'
    
    print(f'\nAugmented prompt to be:\n{augmented_prompt}')
        
    async with ctx.typing():
        is_inferencing = True
        texts = await inference(augmented_prompt, length=68, nsamples=1)
        
    # process text
    response = texts[0]
    print(f'\nResponse:\n{response}')
    
    clean_text = ''.join(response.split(split_prompt)[1:]) # split using split prompt
    clean_text = re.sub(' +', ' ', clean_text) #remove multiple spaces
    
    lines = clean_text.split('\n') #split on newline
    
    prev_reply = ''
    reply = ''
    current_user = ''
    repetition_counter = 1
    
    #30 lines of code just so it responds message by message
    first_response = True # no delay for first response
    for line in lines:
        user_match = re.match('<([A-Za-z0-9 ]+)>', line)
        
        if user_match:
            if first_response:
                first_response = False
            else:
                async with ctx.typing():
                    time.sleep((random.random()*5) + 1)
            current_user = user_match.group(1)
            # send previous user's reply on new user
            if reply:
                await ctx.send(reply)
                reply = ''
                # add typing indicator between pauses
                time.sleep((random.random()*3) + 1)
            reply = reply + f'{current_user} Bot says..'
        else:
            if not current_user:
                print('error finding first user')
                continue
            # skip incomplete line (usually at the end of generated response)
            if line.startswith('<'): 
                print('skipping incomplete line')
                continue
            else:
                if line == prev_reply:
                    print('repetition detected')
                    repetition_counter += 1
                    if repetition_counter > 2:
                        await ctx.send('Repetition detected, terminating.')
                        break
                else:
                    prev_reply = line
                reply = reply + '\n' + line
    if reply and not reply.endswith('Bot says..'):
        await ctx.send(reply)
            
    is_inferencing = False

# dictionary of names for users
nicknames = {
    'crmbob5': ['chris'],
    'Wanderer': ['derek', 'drk', 'derek', 'derek'],
    'Pandoge': ['caleb', 'caleb', 'caleb', 'caleb', 'kaleb', 'kalub', 'cleb', 'clb'],
    'BenjiMcmuscles': ['benji', 'adam'],
    'mynameismili': ['mili'],
    'mrbabybob': ['connor', 'connor', 'connor', 'eimer', 'eimer', 'eimer', 'elmer'],
    'ztoms': ['tommy'],
    'blownking': ['bolaji', 'bobo']
}

# method for randomly replying to a user
async def randomMessageReply(message):
    global is_inferencing
    if is_inferencing:
        print('already responding, will not randomly respond')
        return
    # get ctx of message
    ctx = await client.get_context(message)
    # choose random user to reply as
    random_user = random.sample(MAIN_USERS, 1)[0]
    other_user = str(message.author)
    other_user = other_user[:other_user.index('#')]
    if other_user == random_user:
        random_user = random.sample(MAIN_USERS, 4)[2]
    print(f"Randomly replying to {other_user}'s message: {message.content} in channel {message.channel} as {random_user}")
    
    if True:
        # setup historical prompt
        history_prompt = await get_historical_prompt(message, nmessages=3)
        augmented_prompt = history_prompt + f'\n<{random_user}>\n'
        split_prompt = augmented_prompt
    else:
        augmented_prompt = f'<{other_user}>\n{message.content}\n<{random_user}>\n'
        split_prompt = augmented_prompt

    # randomly augment reply with keywords
    try:
        name = random.sample(nicknames[other_user], 1)[0]
        roll = random.randint(0,23)
    except:
        #if no nickname, change roll
        roll = random.randint(8,23)

    if roll < 2:
        augmented_prompt = augmented_prompt + f'{name}'
    elif roll == 3:
        augmented_prompt = augmented_prompt + f'{name} you'
    elif roll == 4:
        augmented_prompt = augmented_prompt + f'{name} is'
    elif roll == 5:
        augmented_prompt = augmented_prompt + f'is {name}'
    elif roll < 7:
        augmented_prompt = augmented_prompt + f'@{other_user}'
    elif roll == 8:
        augmented_prompt = augmented_prompt + f'@{other_user} you'
    elif roll == 9:
        augmented_prompt = augmented_prompt + f'@{other_user} what'
    elif roll == 10:
        augmented_prompt = augmented_prompt + f'@{other_user} @'
    elif roll == 11:
        augmented_prompt = augmented_prompt + f'@{other_user} how'
    elif roll == 12:
        augmented_prompt = augmented_prompt + f'what'
    elif roll == 13:
        augmented_prompt = augmented_prompt + f'can'
    elif roll == 14:
        augmented_prompt = augmented_prompt + f'is'
    elif roll == 15:
        augmented_prompt = augmented_prompt + f'are'
    else:
        pass
    
    print(f'\nReply roll: {roll} Augmented prompt to be:\n{augmented_prompt}')
    
    # generate responses
    async with ctx.typing():
        is_inferencing = True
        texts = await inference(augmented_prompt, length=50, nsamples=2)
    # filter texts
    filtered_responses = filter_texts(texts, split_prompt)
    # pick a text
    response = random.sample(filtered_responses, 1)[0]
    
    
    lines = response.split('\n') #split on newline and limit num of lines in response
    intro_line = f'{random_user} Bot says..'
    lines = [intro_line] + lines
    response = '\n'.join(lines) #limit # of lines
    
    print(f'Chosen reply:\n{response}')
    await message.channel.send(response)
    is_inferencing = False

print('running client')
#inactive token for demonstration purposes
client.run('Nzc2NjE2NDczODg3NTA2NDUy.X63edA.fogKyKzlOKhnp8TJrtsGMceAx54')