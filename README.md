# GPT2 Discord Bot - Version Marcello
One day, a piece of code decided to name itself Marcello. And so began the artificial intelligence revolution.

Just kidding. I think. This repo is actually a Discord bot I made that generates its responses based on a custom-tuned GPT-2 model

## The Idea
In late 2020, I read this blog post: https://minimaxir.com/2019/09/howto-gpt2/

The great idea then popped into my head: what if I downloaded all the chat history from a Discord channel my friends use and train GPT-2 on it? Why have friends when I can just message the AI-version of my friends? Or better yet- what if I packaged this version of GPT2 into a Discord bot and deployed to the actual server to meet my friends? I pondered just how politically incorrect this version of GPT2 would turn out to be, and that provided even more motivation to get this project done. 

## The data
From the Discord server I ended up with about 1KB of chat history, which I would need to reformat for GPT2 finetuning. I won't be uploading any of the training data or final GPT2 models, due to privacy concerns in addition to the high likelihood of getting cancelled. 
I experimented with several formats of the Discord data for training GPT2, and the one I ended up using is the following:
&ltuser1&gt message &ltuser2&gt message
This required some extra processing when reformatting for the Discord bot but GPT2 seemed to handle its finetuning fine with this format.

## Features
1. Ask the GPT2 version of a user a question
2. Ask GPT2 anything, GPT2 will pretend to be a random user responding
3. Ask GPT2 something, GPT2 will unleash a torrent of messages from bot-versions of users as if a portal to a Discord server in a parallel universe opened up.

## Running the bot
1. Install `gpt_2_simple` and `discord.py` in a Python 3 environment
2. Put a trained gpt2 checkpoint/model in the /checkpoint folder, modify the code to point towards that model
3. Put your Discord bot token in the client.run() command
4. `python friend_bot.py`
