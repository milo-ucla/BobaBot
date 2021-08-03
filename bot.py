#!/usr/bin/env python3
import discord
import os
import requests
import json
from dotenv import load_dotenv

import random
import spacy
nlp = spacy.load("en_core_web_sm")
client = discord.Client()
load_dotenv()

def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q']
    doc = nlp(quote)
    message = quote
    first = True
    tog = True
    print(quote)
    for token in doc:
        if token.pos_ == "NOUN" and tog:
            if(first):
                message = message.replace(str(token), "Boba")
                message = message.replace(str(token).lower(), "boba")
                first = False
            else:
                message = message.replace(str(token), "boba")
        
        if(token.pos_ == "PUNCT" and str(token) != ','):
            first = True
        else: 
            first = False
            
        if(token.pos_ == "NOUN"):
            tog = not tog
    return(message + " - BobaBot")
#to fix a bug where substrings of longer words are replaced with "boba" (like act -> boba, character -> charbobaer ), add 
#all of the nouns to a list and then sort by size before replacing


@client.event
async def on_ready():
    print('Ready to count boba intake as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!quote'):
        my_message = get_quote()
        await message.channel.send(my_message)

    if message.content.startswith('!boba?'):
        my_message = "I can't say, not until Milo codes this bot better"
        if(random.choice([0,1]) == 1):
            my_message = "Yes, go get some boba!"
        else:
            my_message = "Nah, not today"
        await message.channel.send(my_message)

    elif message.content.startswith('!boba'):
        my_message = "I love boba!"
        await message.channel.send(my_message)

client.run(os.getenv('TOKEN'))