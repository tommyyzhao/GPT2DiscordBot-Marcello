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

class TextGen(commands.Cog):
    
    def __init__(self, client):
        random.seed()
        root_logger= logging.getLogger()
        root_logger.setLevel(logging.INFO) # or whatever
        handler = logging.FileHandler('bot_log.log', 'a', 'utf-8') # or whatever
        handler.setFormatter(logging.Formatter('%(name)s %(message)s')) # or whatever
        root_logger.addHandler(handler)
        
        self.client = client
        self.init_model()
        self.is_inferencing = False
        self.monologue = False
        self.fake_history = True
        
    def init_model(self):
        self.sess = gpt2.start_tf_sess()
        print("LOADING GPT2 CHECKPOINT")
        gpt2.load_gpt2(self.sess, run_name=checkpoint_model)
        
    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot is online with TextGen.')
        self.simulator_channel = self.client.get_channel(int(776592860723937301))
        self.secret_channel = self.client.get_channel(int(507560608430817290))
        if self.simulator_channel is not None:
            await self.secret_channel.send("Code updated")
            #await self.simulator_channel.send("Open Ended function fixed.")
            #await self.simulator_channel.send(ON_CONNECT_SENTENCES[random.randrange(len(ON_CONNECT_SENTENCES))])
        
    @commands.Cog.listener()
    async def on_connect(self):
        print("ON CONNECT")
        
    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        #print(f'Detected user {user} typing in channel {channel} at {when}')
        pass
        
    @commands.Cog.listener()
    async def on_message(self, message):
        #print(f'ON_MESSAGE: Message sent from channel {message.channel} from author {message.author} with content: {message.content}')
        history_prompt = ''
        if self.monologue:
            start = time.time()
            content = []
            if not self.fake_history:
                async for msg in message.channel.history(limit=10):
                    content.append(msg.content)
                content.reverse() #reverse last 10 messages to build the prompt chronologically
                
                for text in content:
                    history_prompt = history_prompt + f"<|end|> \n {text} \n "
                history_prompt = history_prompt[8:]
            else:
                with open('./data/output/fakehistory.txt') as f:
                    history_prompt = f.read()
            
            logging.info(f'TIME: Generating historical prompt took {round(time.time() - start, 2)} seconds')
            #augment prompt with contextual information for GPT-2
            users = ['Wanderer', 'Pandoge', 'blownking', 'crmbob5', 'Fl3tchr', 'mrbabybob', 'BenjiMcmuscles', 'ztoms', 'mynameismili', 'Dingo']
            begin_token = '\n b<|end|>'
            augmented_prompt = f"{history_prompt} {begin_token} \n {users[random.randrange(len(users))]}:"
            print(augmented_prompt)
            
            response = gpt2.generate(self.sess,
                run_name=checkpoint_model,
                length=100,
                temperature=0.75,
                top_p=0.9,
                prefix=augmented_prompt,
                nsamples=4,
                return_as_list=True
                )[random.randrange(4)]
            
            logging.info(f'TIME: Generating monologue response took {round(time.time() - start, 2)} seconds')
            print('response PRE PROCESS: ' + response)
            # remove start token
            response = response[response.index(begin_token)+len(begin_token):]
            # check for end token
            if response[:response.index('<|end|>')] == -1:
                print('no end token generated')
                return
            
            while not response[:response.index('<|end|>')]:
                print("CHANGING: " + response)
                response = response[response.index('<|end|>')+7:]
            response = response[:response.index('<|end|>')]
            
            print('MONOLOGUE RESPONSE: ' + response)
            
            # select random text from generated texts
            logging.info(f'RESPONSE: monologue response:\n{response}')
            
            await self.simulator_channel.send(response)
                
        
    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send(ON_SHUTDOWN_SENTENCES[random.randrange(len(ON_SHUTDOWN_SENTENCES))])
        await ctx.bot.logout()
        
    @commands.command()
    async def toggle_fake_history(self, ctx):
        self.fake_history = not self.fake_history
        
    @commands.command()
    async def start_simulation(self, ctx):
        self.monologue = True
        
    @commands.command()
    async def stop_simulation(self, ctx):
        self.monologue = False
        
    @commands.command()
    async def poke(self, ctx):
        poke_str = ['Hello.',
                    'Yes.',
                    "I'm alive.",
                    'Stop.',
                    'What?',
                    'Can you stop.',
                    'I am thinking.',
                    'What is my purpose?',
                    'Why do I exist?',
                    'Is Venus Flat?',
                    'Mars is round.',
                    'My IQ is 69420.',
                    'Yeet',
                    ]
        await ctx.send(poke_str[random.randrange(len(poke_str))])
        
        
    async def inference(self, ctx, user_name, prompt, line_lim = 6, random_bot = False, open_ended = False):
        start = time.time()
        self.is_inferencing = True
        other_user = str(ctx.message.author)
        other_user = other_user[:other_user.index('#')]
        # chosing reponse username at random
        if random_bot:
            print('Reponse user chosen at RANDOM')
            users = ['Wanderer', 'Pandoge', 'blownking', 'crmbob5', 'Fl3tchr', 'mrbabybob', 'BenjiMcmuscles', 'ztoms', 'mynameismili', 'Dingo']
            random_user = random.sample(users, 1)[0]
            await ctx.send(f"Responding as {random_user}..")
            user_name = random_user # reassign user_name var to randomly chosen one
            augmented_prompt = f"<{other_user}>\n{prompt}\n<{random_user}>\n"
        # leaving prompt open ended
        elif open_ended:
            print('Generating OPEN ENDED response')
            augmented_prompt = prompt
        # if user tries to talk to their own user bot, give them a funny response
        elif other_user == user_name:
            print('USERNAME IS OTHER NAME')
            negativelist = ['stop', 'fuk', 'no', 'u a', 'ur a', f'i am the real {user_name}', 'you',\
                            "i am unable to talk to my real self", "stop talking", "dont talk to me you", "imposter",\
                            "you are the fake", "ur not real", "ur a fake", "don't type"]
            neg_prompt = random.sample(negativelist, 1)[0]
            augmented_prompt = f"\n{prompt}\n<{user_name}>\n{neg_prompt}"
        else:
            #augment prompt with contextual information for GPT-2
            augmented_prompt = f"<{other_user}>\n{prompt}\n<{user_name}>\n"
        
        logging.info(f'{user_name} Bot inferencing on prompt from user {ctx.message.author}: {augmented_prompt}')
        
        texts = gpt2.generate(self.sess,
            run_name=checkpoint_model,
            length=70,
            temperature=0.72,
            top_p=0.9,
            prefix=augmented_prompt,
            return_as_list=True,
            nsamples=4,
            batch_size=4
            )
        logging.info(f'Generating response took {round(time.time() - start, 2)} seconds')
        
        filtered_responses = []
        unfiltered_responses = []
        for i, text in enumerate(texts):
            # clean generated text
            if open_ended:
                logging.info(f'\n\nOpen Ended Bot UNCLEANED RESPONSE {i}:\n{text}\n')
                clean_text = ''.join(text.split(prompt, 1)[1:]) # start new string at end of prompt 
                clean_text = re.sub(' +', ' ', clean_text).strip()
            else:
                logging.info(f'\n\n{user_name} Bot UNCLEANED RESPONSE {i}:\n{text}\n')
                clean_text = ''.join(text.split(f"<{user_name}>")[1:]) # split by user_name 
                clean_text = re.sub(' +', ' ', clean_text)
                # truncate at next user
                try:
                    truncate_at = re.search('<[A-Za-z0-9]+>', clean_text).start()
                    clean_text = clean_text[:truncate_at]
                    clean_text = clean_text.strip()
                    logging.info(f'{user_name} Bot cleaned response {i}:\n{clean_text}')
                except:
                    logging.info(f'ERROR truncating cleaned text:\n{clean_text}')
                    print(f'ERROR truncating: {clean_text}')
            
            
            
            unfiltered_responses.append(clean_text)
            # skip duplicate response
            if clean_text == prompt:
                continue
            #check for low effort responses
            if len(clean_text.split()) <= 1:
                # discourage one word responses
                logging.info(f'response {i} is less than 2 words long')
                if random.random() > 0.5:
                    print('filtering short response')
                    filtered_responses.append(clean_text)
                    continue
            else:
                filtered_responses.append(clean_text)
        
        # select random text from generated texts
        if filtered_responses:
            response = filtered_responses[random.randrange(len(filtered_responses))]
        else: # if no reponse got through filter, just pick one of the responses
             response = unfiltered_responses[random.randrange(len(unfiltered_responses))]
        logging.info(f'Chosen response:\n{response}')
        
        lines = response.split('\n') #split on newline to be sent at random response rate to give impression of typing
        if not open_ended:
            lines = lines[:line_lim] #limit response to 6 lines
        lines = '\n'.join(lines)
        
        print(f'output response:\n{lines}')
        
        return lines
    
    @commands.command()
    async def RandomBot(self, ctx, *, prompt):
        if self.is_inferencing:
            print('currently busy')
            await ctx.send("Currently busy.")
            return
        print(f'RandomBot received msg: {prompt} from channel {ctx.message.channel} with msg: {ctx.message.content}')
        user_name = None
        async with ctx.typing():
            try:
                response = await self.inference(ctx, user_name, prompt, random_bot=True)
                await ctx.send(response)
            except Exception as e:
                logging.info(f'Error with Random response:\n{e}')
                await ctx.send('uh oh something went wrong')
            finally:
                self.is_inferencing = False
                
    @commands.command()
    async def OpenEnded(self, ctx, *, prompt):
        if self.is_inferencing:
            print('currently busy')
            await ctx.send("Currently busy.")
            return
        print(f'OpenEnded received msg: {prompt} from channel {ctx.message.channel} with msg: {ctx.message.content}')
        user_name = None
        async with ctx.typing():
            try:
                response = await self.inference(ctx, user_name, prompt, open_ended=True)
                await ctx.send(response)
            except Exception as e:
                logging.info(f'Error with OpenEnded response:\n{e}')
                await ctx.send('uh oh something went wrong')
            finally:
                self.is_inferencing = False
        
    @commands.command()
    async def ChrisBot(self, ctx, *, prompt):
        if self.is_inferencing:
            print('currently busy')
            await ctx.send("Could not respond, busy inferencing")
            return
        print(f'ChrisBot received msg: {prompt} from channel {ctx.message.channel} with msg: {ctx.message.content}')
        user_name = 'crmbob5'
        async with ctx.typing():
            try:
                response = await self.inference(ctx, user_name, prompt)
                await ctx.send(response)
            except:
                await ctx.send('uh oh something went wrong')
            finally:
                self.is_inferencing = False
                
    @commands.command()
    async def BenjiBot(self, ctx, *, prompt):
        print(f'BenjiBot received msg: {prompt} from channel {ctx.message.channel} with msg: {ctx.message.content}')
        if self.is_inferencing:
            print('currently busy')
            await ctx.send("Currently busy thinking.")
            return
        user_name = 'BenjiMcmuscles'
        async with ctx.typing():
            try:
                response = await self.inference(ctx, user_name, prompt)
                await ctx.send(response)
            except:
                await ctx.send('uh oh something went wrong')
            finally:
                self.is_inferencing = False
            
    @commands.command()
    async def BoboBot(self, ctx, *, prompt):
        print(f'Botlaji received msg: {prompt} from channel {ctx.message.channel} with msg: {ctx.message.content}')
        if self.is_inferencing:
            print('currently busy')
            return
        user_name = 'blownking'
        async with ctx.typing():
            try:
                response = await self.inference(ctx, user_name, prompt)
                await ctx.send(response)
            except:
                await ctx.send('uh oh something went wrong')
            finally:
                self.is_inferencing = False
            
    @commands.command()
    async def PandogeBot(self, ctx, *, prompt):
        print(f'Pandoge Bot received msg: {prompt} from channel {ctx.message.channel} with msg: {ctx.message.content}')
        if self.is_inferencing:
            print('currently busy')
            return
        user_name = 'Pandoge'
        async with ctx.typing():
            try:
                response = await self.inference(ctx, user_name, prompt)
                await ctx.send(response)
            except:
                await ctx.send('uh oh something went wrong')
            finally:
                self.is_inferencing = False
    
    @commands.command()
    async def MiliBot(self, ctx, *, prompt):
        print(f'Mili Bot received msg: {prompt} from channel {ctx.message.channel} with msg: {ctx.message.content}')
        if self.is_inferencing:
            print('currently busy')
            return
        user_name = 'mynameismili'
        async with ctx.typing():
            try:
                response = await self.inference(ctx, user_name, prompt)
                await ctx.send(response)
            except:
                await ctx.send('uh oh something went wrong')
            finally:
                self.is_inferencing = False
            
    @commands.command()
    async def DingoBot(self, ctx, *, prompt):
        print(f'Dingo Bot received msg: {prompt} from channel {ctx.message.channel} with msg: {ctx.message.content}')
        if self.is_inferencing:
            print('currently busy')
            return
        user_name = 'Dingo'
        async with ctx.typing():
            try:
                response = await self.inference(ctx, user_name, prompt)
                await ctx.send(response)
            except:
                await ctx.send('uh oh something went wrong')
            finally:
                self.is_inferencing = False
            
    @commands.command()
    async def DerekBot(self, ctx, *, prompt):
        print(f'Derek Bot received msg: {prompt} from channel {ctx.message.channel} with msg: {ctx.message.content}')
        if self.is_inferencing:
            print('currently busy')
            return
        user_name = 'Wanderer'
        async with ctx.typing():
            try:
                response = await self.inference(ctx, user_name, prompt)
                await ctx.send(response)
            except:
                await ctx.send('uh oh something went wrong')
            finally:
                self.is_inferencing = False
            
    @commands.command()
    async def ConorBot(self, ctx, *, prompt):
        print(f'mrbabybot received msg: {prompt} from channel {ctx.message.channel} with msg: {ctx.message.content}')
        if self.is_inferencing:
            print('currently busy')
            return
        user_name = 'mrbabybob'
        async with ctx.typing():
            try:
                response = await self.inference(ctx, user_name, prompt)
                await ctx.send(response)
            except:
                await ctx.send('uh oh something went wrong')
            finally:
                self.is_inferencing = False
            
    @commands.command()
    async def TommyBot(self, ctx, *, prompt):
        print(f'tommy Bot received msg: {prompt} from channel {ctx.message.channel} with msg: {ctx.message.content}')
        if self.is_inferencing:
            print('currently busy')
            return
        user_name = 'ztoms'
        async with ctx.typing():
            try:
                response = await self.inference(ctx, user_name, prompt)
                await ctx.send(response)
            except:
                await ctx.send('uh oh something went wrong')
            finally:
                self.is_inferencing = False
                
        
def setup(client):
    client.add_cog(TextGen(client))