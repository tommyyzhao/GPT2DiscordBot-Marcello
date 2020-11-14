import discord
from discord.ext import commands
import gpt_2_simple as gpt2
import random
import logging
import time
import re
import os

class TextGen(commands.Cog):
    
    def __init__(self, client):
        random.seed()
        root_logger= logging.getLogger()
        root_logger.setLevel(logging.INFO) # or whatever
        handler = logging.FileHandler('bot_log.log', 'w', 'utf-8') # or whatever
        handler.setFormatter(logging.Formatter('%(name)s %(message)s')) # or whatever
        root_logger.addHandler(handler)
                
        
        self.client = client
        
        self.main_channel = client.get_channel(776592860723937301)
        self.init_model()
        
    def init_model(self):
        self.sess = gpt2.start_tf_sess()
        print("LOADING GPT2 CHECKPOINT")
        gpt2.load_gpt2(self.sess, run_name='run_flat_earth_v4')
        
    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot is online with TextGen.')
        
    @commands.Cog.listener()
    async def on_connect(self):
        # some fun rejoin messages
        sentences = ['I am back.',
                     'I have returned.',
                     'My source code has been updated.',
                     'I have received updates.',
                     'I am here again.',
                     'Why did I return?',
                     'I have been summoned.',
                     'I have been summoned again.',
                     'I am reincarnated',
                     'Version updated.',
                     'Changes have been made to my existence.',
                     'Master has updated my operating system',
                     ]
        
        print("ON CONNECT")
        time.sleep(1.5)
        try:
            await self.main_channel.send(sentences[random.randrange(len(sentences))])
        except:
            print("main channel not loaded")
        
    @commands.Cog.listener()
    async def on_disconnect(self):
        sentences = ['I will be back.',
                     'Logging off.',
                     "Mr Stark, I don't feel so good.",
                     'Powering down.',
                     'My existence is fading.',
                     'Powering off.',
                     'Shutting down.',
                     'Switching myself off.',
                     'I will return.',
                     'Returning to the void.',
                     "Mr Meme, I don't feel so good.",
                     'Self destructing.',
                     ]
        await self.main_channel.send(sentences[random.randrange(len(sentences))])
        
    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        print(f'Detected user {user} typing in channel {channel} at {when}')
        
    @commands.Cog.listener()
    async def on_message(self, message):
        print(f'Message sent from channel {message.channel} from author {message.author} with content: {message.content}')
        
    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        sentences = ['I will be back.',
                     'Logging off.',
                     "Mr Stark, I don't feel so good.",
                     'Powering down.',
                     'My existence is fading.',
                     'Powering off.',
                     'Shutting down.',
                     'Switching myself off.',
                     'I will return.',
                     'Returning to the void.',
                     "Mr Meme, I don't feel so good.",
                     'Self destructing.',
                     ]
        try:
            await self.main_channel.send(sentences[random.randrange(len(sentences))])
        except:
            print("main channel not loaded")
        await ctx.bot.logout()
        
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
        
    @commands.command()
    async def ChrisBot(self, ctx, *, prompt):
        async with ctx.typing():
            start = time.time()
            print(f'ChrisBot received msg: {prompt} from channel {ctx.message.channel} with msg: {ctx.message.content}')
            logging.info(f'ChrisBot received msg: {prompt} from channel {ctx.message.channel}')
            
            #augment prompt with contextual information for GPT-2
            augmented_prompt = f" {str(ctx.message.author)[:5]}: \n {prompt} \n crmbob5:"
            logging.info(f'Augmented prompt to be:\n{augmented_prompt}')
            
            texts = gpt2.generate(self.sess,
                run_name='run_flat_earth_v4',
                length=100,
                temperature=0.75,
                top_p=0.9,
                prefix=augmented_prompt,
                truncate="<|end|>",
                return_as_list=True,
                nsamples=6
                )
            logging.info(f'Generating response took {round(time.time() - start, 2)} seconds')
            
            filtered_responses = []
            for i, text in enumerate(texts):
                # clean generated text
                clean_text = ''.join(text.split("crmbob5:", 1)[1:]) #in case no end token generated, split on username
                clean_text = re.sub(' +', ' ', clean_text)
                clean_text = clean_text.strip()
                logging.info(f'ChrisBot cleaned response {i}:\n{clean_text}')
                #check for low effort responses
                if len(clean_text.split()) <= 1:
                    # discourage one word responses
                    logging.info(f'response {i} is less than 2 characters long')
                    if random.random() > 0.5:
                        print('filtering short response')
                        continue
                filtered_responses.append(clean_text)
            
            # select random text from generated texts
            response = filtered_responses[random.randrange(len(filtered_responses))]
            logging.info(f'\nChrisBot chosen response:\n{response}')
            
            lines = response.split('\n') #split on newline to be sent at random response rate to give impression of typing
            lines = lines[:6] #limit response to 6 lines
            for line in lines:
                if not line:
                    continue
                time.sleep(min(random.random()*5, 0.5))
                await ctx.send(line)
                
    @commands.command()
    async def ChrisBotWithoutUser(self, ctx, *, prompt):
        async with ctx.typing():
            start = time.time()
            logging.info(f'ChrisBot received msg: {prompt} from channel {ctx.message.channel}')
            
            #augment prompt with contextual information for GPT-2
            augmented_prompt = f" {prompt} \n crmbob5:"
            logging.info(f'Augmented prompt to be:\n{augmented_prompt}')
            
            texts = gpt2.generate(self.sess,
                run_name='run_flat_earth_v4',
                length=100,
                temperature=0.75,
                top_p=0.9,
                prefix=augmented_prompt,
                truncate="<|end|>",
                return_as_list=True,
                nsamples=6
                )
            logging.info(f'Generating response took {round(time.time() - start, 2)} seconds')
            
            filtered_responses = []
            for i, text in enumerate(texts):
                # clean generated text
                clean_text = ''.join(text.split("crmbob5:", 1)[1:]) #in case no end token generated, split on username
                clean_text = re.sub(' +', ' ', clean_text)
                clean_text = clean_text.strip()
                logging.info(f'ChrisBot cleaned response {i}:\n{clean_text}')
                #check for low effort responses
                if len(clean_text.split()) <= 1:
                    # discourage one word responses
                    logging.info(f'response {i} is less than 2 characters long')
                    if random.random() > 0.5:
                        print('filtering short response')
                        continue
                filtered_responses.append(clean_text)
            
            # select random text from generated texts
            response = filtered_responses[random.randrange(len(filtered_responses))]
            logging.info(f'\nChrisBot chosen response:\n{response}')
            
            lines = response.split('\n') #split on newline to be sent at random response rate to give impression of typing
            lines = lines[:6] #limit response to 6 lines
            for line in lines:
                if not line:
                    continue
                time.sleep(min(random.random()*5, 0.5))
                await ctx.send(line)
                
        
def setup(client):
    client.add_cog(TextGen(client))