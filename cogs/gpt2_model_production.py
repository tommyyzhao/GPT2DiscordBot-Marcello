import discord
from discord.ext import commands
import gpt_2_simple as gpt2
import random
import logging
import time
import re
import os

memeland_telegraph = "203186554624147457"
secretbox = "507560608430817290"

checkpoint_model = 'run_flat_earth_355M_v2.2'
# some fun rejoin messages
ON_CONNECT_SENTENCES = ['I am back.',
                     'I have returned.',
                     'My source code has been updated.',
                     'I have received updates.',
                     'Code updated.',
                     ':mechanical_arm:',
                     'I have been summoned.',
                     'I have been summoned again.',
                     'I am reincarnated',
                     'Version updated.',
                     'Changes have been made to my existence.',
                     'Operating system updated',
                     ]

ON_SHUTDOWN_SENTENCES = ['I will be back.',
                     'Logging off.',
                     'Powering down.',
                     'My existence is fading.',
                     'Powering off.',
                     'Shutting down.',
                     'Switching off.',
                     'I will return.',
                     'Returning to the void.',
                     'Self destructing.',
                     ]

MAIN_USERS = ['Wanderer', 'Pandoge', 'blownking', 'crmbob5', 'Fl3tchr', 'mrbabybob', 'BenjiMcmuscles', 'ztoms', 'mynameismili']

class TextGen(commands.Cog):
    
    def __init__(self, client):
        random.seed()
        root_logger= logging.getLogger()
        root_logger.setLevel(logging.INFO) # or whatever
        handler = logging.FileHandler('bot_log.log', 'a', 'utf-8') # or whatever
        handler.setFormatter(logging.Formatter('%(message)s')) # or whatever
        root_logger.addHandler(handler)
        
        self.client = client
        self.init_model()
        self.temperature = 0.75
        self.is_inferencing = False
        self.use_history = False
        self.use_bothistory = True
        self.REPLY_CHANCE = 0.1
        self.BOT_LINE_LIMIT = 8
        
    def init_model(self):
        self.sess = gpt2.start_tf_sess()
        gpt2.load_gpt2(self.sess, run_name=checkpoint_model)
        
    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot is online with TextGen.')
        self.simulator_channel = self.client.get_channel(int(776592860723937301))
        self.secret_channel = self.client.get_channel(int(507560608430817290))
        if self.simulator_channel is not None:
            await self.secret_channel.send("Code updated")
            #await self.simulator_channel.send("Language model 3.1 loaded.")
            #await self.simulator_channel.send(ON_CONNECT_SENTENCES[random.randrange(len(ON_CONNECT_SENTENCES))])
        
    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        #print(f'Detected user {user} typing in channel {channel} at {when}')
        pass
        
    @commands.Cog.listener()
    async def on_message(self, message):
        random.seed()
        if not message.content.startswith('.') and random.random() < self.REPLY_CHANCE and not str(message.author).startswith('Intellectual'):
            print('on message triggered')
            await self.randomMessageReply(message)
        #await message.channel.send(response)
                
    
    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send(ON_SHUTDOWN_SENTENCES[random.randrange(len(ON_SHUTDOWN_SENTENCES))])
        await ctx.bot.logout()
        
    @commands.command()
    async def setTemp(self, ctx, temp):
        try:
            t = min(float(temp), 1)
        except:
            await ctx.send("invalid temperature")
        self.temperature = t
        await ctx.send(f"Changed GPT2 temperature setting to {t}.")
        
    @commands.command()
    async def setReplyChance(self, ctx, chance):
        try:
            new_chance = min(float(chance), 1)
        except:
            await ctx.send("invalid input")
        self.REPLY_CHANCE = new_chance
        await ctx.send(f"Changed reply chance to {new_chance}.")
        
    @commands.command()
    async def useHistory(self, ctx):
        self.use_history = not self.use_history
        await ctx.send(f"Using message history: {self.use_history}")
        
        
    @commands.command()
    async def useBotHistory(self, ctx):
        self.use_bothistory = not self.use_bothistory
        await ctx.send(f"Using bot messages as history: {self.use_bothistory}")
        
    @commands.command()
    async def poke(self, ctx):
        poke_str = ['Hello.', 'Yes.', "I'm alive.", 'Stop.', 'What?',
                    'Can you stop', 'I am thinking.', 'What is my purpose?',
                    'Why do I exist?', 'Is Venus Flat?', 'Mars is round.',
                    'My IQ is 69420.', 'Yeet']
        await ctx.send(random.sample(poke_str, 1)[0])
        
    async def randomMessageReply(self, message):
        self.is_inferencing = True
        # choose random user to reply as
        random_user = random.sample(MAIN_USERS, 1)[0]
        other_user = str(message.author)
        other_user = other_user[:other_user.index('#')]
        logging.info(f"Randomly replying to {other_user}'s message: {message.content} in channel {message.channel} as {random_user}")
        
        
        if self.use_history:
            # setup historical prompt
            history_prompt = await self.get_historical_prompt(message, nmessages=15)
            augmented_prompt = history_prompt + f'\n<{random_user}>'
        else:
            augmented_prompt = f'<{other_user}>\n{message.content}\n<{random_user}>\n'
            
        logging.info(f'Augmented prompt to be:\n{augmented_prompt}')
        
        # generate responses
        texts = await self.inference(augmented_prompt, length=50)
        # filter texts
        filtered_responses = self.filter_texts(texts, random_user)
        # pick a text
        response = random.sample(filtered_responses, 1)[0]
        
        logging.info(f'Chosen response:\n{response}')
        
        lines = response.split('\n') #split on newline and limit num of lines in response
        intro_line = f'{random_user} Bot says..'
        lines = [intro_line] + lines
        response = '\n'.join(lines[:self.BOT_LINE_LIMIT]) #limit # lines
        
        print(f'Output response:\n{response}')
        await message.channel.send(response)
        self.is_inferencing = False
    
        
    async def inference(self, prompt, length=100, nsamples=4):
        start = time.time()        
        logging.info(f'INFERENCING on prompt:\n{prompt}\n')
        
        texts = gpt2.generate(self.sess,
            run_name=checkpoint_model,
            length=length,
            temperature=self.temperature,
            top_p=0.9,
            prefix=prompt,
            return_as_list=True,
            nsamples=nsamples,
            batch_size=nsamples
            )
        logging.info(f'INFERENCING {len(texts)} samples took {round(time.time() - start, 2)} seconds\n')
        
        return texts
    
    
    def filter_texts(self, texts, user_name):
        filtered_responses = []
        unfiltered_responses = []
        
        for i, text in enumerate(texts):
            # clean generated text
            logging.info(f'\nUNCLEANED RESPONSE {i}:\n{text}\n')
            clean_text = ''.join(text.split(f"<{user_name}>")[1:]) # split by user_name 
            clean_text = re.sub(' +', ' ', clean_text) #remove multiple spaces
            # truncate at next user
            try:
                truncate_at = re.search('<[A-Za-z0-9 ]+>', clean_text).start() #find the next user's string
                clean_text = clean_text[:truncate_at].strip()
                logging.info(f'\nCLEANED RESPONSE {i}:\n{clean_text}')
                if not clean_text:
                    logging.info(f'\nCLEANED RESPONSE {i} is empty, skipping')
                    continue
            except:
                logging.info(f'ERROR truncating cleaned text:\n{clean_text}')
                print(f'ERROR truncating: {clean_text}')
                continue
            
            unfiltered_responses.append(clean_text)
            #check for low effort responses
            if len(clean_text.split()) <= 1:
                # discourage one word responses
                allowed = ['no', 'yes', 'sure']
                if clean_text.split()[0] not in allowed and random.random() > 0.25:
                    print('filtering short response')
                    logging.info(f'Response {i}: {clean_text} is less than a word long, filtering')
                    filtered_responses.append(clean_text)
                    continue
            else:
                filtered_responses.append(clean_text)
                
        if filtered_responses:
            return filtered_responses
        else:
            return unfiltered_responses
            
    async def get_historical_prompt(self, ctx, nmessages = 10):
        prior_messages = []
        async for msg in ctx.channel.history(limit=nmessages):
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
                for line in text.split('\n'):
                    if line.endswith('Bot says..'):
                        simulated = True
                        simulated_user = line.replace('Bot says..', '').strip()
                        prev_author = simulated_user
                        history_prompt = history_prompt + f'<{simulated_user}>\n'
                    elif simulated:
                        history_prompt = history_prompt + f'{line}\n'
                continue
            
            #clean bot commands from message content
            text = re.sub(r'^\.[A-Za-z]+', '', text).strip()
            if not text:
                continue #skip empty messages
            
            if author_name != prev_author:
                history_prompt = history_prompt + f'<{author_name}>\n{text}\n'
                prev_author = author_name
            else:
                history_prompt = history_prompt + f'{text}\n'
            
        return history_prompt
    
    @commands.command()
    async def LogHistoricalPrompt(self, ctx):
        prompt = await self.get_historical_prompt(ctx, nmessages=15)
        logging.info(f"\n\nHISTORICAL PROMPT:\n{prompt}")
        print('logged historical prompt')
            
    @commands.command()
    async def bot(self, ctx, user_name, *, prompt):
        if self.is_inferencing:
            await ctx.send("Could not respond, already responding")
            return
        
        print(f'bot command received msg: {prompt} from channel {ctx.message.channel} with msg: {ctx.message.content}')
        logging.info(f'\nbot command received MSG: {ctx.message.content} from CHANNEL: {ctx.message.channel}')
        
        other_user = str(ctx.message.author)
        other_user = other_user[:other_user.index('#')]
            
        async with ctx.typing():
            self.is_inferencing = True
            augmented_prompt = f'<{other_user}>\n{prompt}\n<{user_name}>\n'
            logging.info(f'Augmented prompt to be:\n{augmented_prompt}')
            texts = await self.inference(augmented_prompt, length=50)
            
        filtered_responses = self.filter_texts(texts, user_name)
        # process text
        response = random.sample(filtered_responses, 1)[0]
        
        logging.info(f'Chosen response:\n{response}')
        
        lines = response.split('\n') #split on newline and limit num of lines in response
        
        intro_line = f'{user_name} Bot says..'
        lines = [intro_line] + lines
        
        response = '\n'.join(lines[:self.BOT_LINE_LIMIT]) #limit # lines
        
        print(f'Output response:\n{response}')
        
        await ctx.send(response)
        self.is_inferencing = False
        
        
    @commands.command()
    async def multiverse(self, ctx, *, prompt):
        if self.is_inferencing:
            await ctx.send("Could not respond, already responding")
            return
        
        print(f'MULTIVERSE command received msg: {prompt} from channel {ctx.message.channel} with msg: {ctx.message.content}')
        logging.info(f'\nMULTIVERSE command received MSG: {ctx.message.content} from CHANNEL: {ctx.message.channel}')
        
        other_user = str(ctx.message.author)
        other_user = other_user[:other_user.index('#')]
        random_user = random.sample(MAIN_USERS, 1)[0]
        split_prompt = '' # prompt to split the generated response on
        
        if self.use_history:
            # setup historical prompt
            history_prompt = await self.get_historical_prompt(ctx.message, nmessages=15)
            print('historical prompt is:\n' + history_prompt)
            augmented_prompt = history_prompt + f'<{random_user}>'
            split_prompt = history_prompt
        else:
            augmented_prompt = f'{prompt}\n<{random_user}>\n'
            split_prompt = f'{prompt}\n'
        
        logging.info(f'Augmented prompt to be:\n{augmented_prompt}')
            
        async with ctx.typing():
            self.is_inferencing = True
            texts = await self.inference(augmented_prompt, length=65, nsamples=1)
            
        # process text
        response = texts[0]
        logging.info(f'Chosen response:\n{response}')
        
        clean_text = ''.join(response.split(split_prompt)[1:]) # split using split prompt
        clean_text = re.sub(' +', ' ', clean_text) #remove multiple spaces
        
        lines = clean_text.split('\n') #split on newline
        
        reply = ''
        current_user = ''
        
        for line in lines:
            user_match = re.match('<([A-Za-z0-9 ]+)>', line)
            
            if user_match:
                async with ctx.typing():
                    time.sleep((random.random()*3) + 1)
                current_user = user_match.group(1)
                # send previous user's reply on new user
                if reply:
                    await ctx.send(reply)
                    reply = ''
                    # add typing indicator between pauses
                    time.sleep((random.random()*2) + 2)
                reply = reply + f'{current_user} Bot says..'
            else:
                if not current_user:
                    print('error finding first user')
                    logging.info('error finding first user in opened ended response')
                    continue
                # skip incomplete line (usually at the end of generated response)
                if line.startswith('<'): 
                    print('skipping incomplete line')
                    continue
                else:
                    reply = reply + '\n' + line
        if reply:
            await ctx.send(reply)
                
        self.is_inferencing = False
                
    
        
def setup(client):
    client.add_cog(TextGen(client))