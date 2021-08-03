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

'''
TO DO
NLP: The part-of-speech is course right now, only identifying NOUN or not
    it should instead be more fine, only replacing parts of speech that can be "boba". 
    Once this is done, the tog bool should be removed or adjusted.

DB: When a user logs boba
'''
def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q']
    print(quote)
    return [quote, json_data[0]['a']]

def bobafy_quote(input: str) -> str:
    message = input
    doc = nlp(input)
    first = True
    tog = True
    replaced = []
    for token in doc:
        if token.pos_ == "NOUN" and tog:
            if(first):
                replaced.append([str(token), "Boba"])
                replaced.append([str(token).lower(), "boba"])
                first = False
            else:
                replaced.append([str(token), "boba"])
        
        if(token.pos_ == "PUNCT" and str(token) != ','):
            first = True
        else: 
            first = False
            
        if(token.pos_ == "NOUN"):
            tog = not tog
    replaced.sort()
    for pair in replaced:
        message = message.replace(pair[0], pair[1])
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
        quote = get_quote()
        my_message = bobafy_quote(quote[0])
        fullquote = quote[0] + " - " + quote[1]
        await message.channel.send(my_message + '\n||' + fullquote +'||')

    if message.content.startswith('!boba?'):
        my_message = "I can't say, not until Milo codes this bot better"
        yn = random.choice([True, False])
        print(yn)
        if(yn):
            my_message = "Yes, go get some boba!"
        else:
            my_message = "Nah, not today"
        await message.channel.send(my_message)

    elif message.content.startswith('!boba'):
        my_message = "I love boba!\n{This feature is under development}"
        await message.channel.send(my_message)

client.run(os.getenv('TOKEN'))