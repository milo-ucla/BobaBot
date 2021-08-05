#!/usr/bin/env python3
import discord
import os
import requests
import json
from dotenv import load_dotenv
from pymongo import MongoClient
import random
import spacy
import re
import hashlib

load_dotenv()

client = discord.Client()

mongoclient = MongoClient(os.getenv("MONGO_URL"))

db = mongoclient.boba_db

boba_count_db = db.boba_count


def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q']
    return [quote, json_data[0]['a']]


def bobafy_quote(message):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(message)
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


def get_count(user):
    user_query = {
            "user": user,
    }
    query_user = boba_count_db.find_one(user_query)
    if query_user is None:
        return 0
    else:
        return query_user["boba_count"]

def update_count(user, increment = 1):
    user_query = {
            "user": user,
    }
    query_user = boba_count_db.find_one(user_query)
    if query_user is None:
        count = increment
        user_query["boba_count"] = count
        boba_count_db.insert_one(user_query)
    else:
        filter = { 'user': user }
        newvalues = { "$set": { 'boba_count': query_user["boba_count"] + increment } }
        boba_count_db.update_one(filter, newvalues) 
        count = query_user["boba_count"] + increment
    return count

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    channel = message.channel.id 
    # TODO: make the database corespond to the server

    username_raw = str(message.author).split("#")[0]
    username = hashlib.sha256(username_raw.encode('utf-8')).hexdigest()
    if message.content.startswith('!boba quote'):
        quote = get_quote()
        my_message = bobafy_quote(quote[0])
        fullquote = quote[0] + " - " + quote[1]
        await message.channel.send(my_message + '\n||' + fullquote +'||')
    
    elif message.content.startswith('!boba?'):
        my_message = "I can't say, not until Milo codes this bot better"
        yn = random.choice([True, False])
        if(yn):
            my_message = "Yes, go get some boba!"
        else:
            my_message = "Nah, not today"
        await message.channel.send(my_message)

    elif message.content.startswith('!boba'):
        word_list = message.content.split(" ")
        if len(word_list) > 2 or word_list[-1] == "help":
            my_message = f"Use the boba count with 1 argument.\nType `count` to get your boba count, type `integer` to add to your boba count (default: 1).\nFor more information, try !boba info"
            await message.channel.send(my_message)
        elif word_list[-1] == "count":
            # user calls !boba count to get their boba count
            count = get_count(username)
            my_message = f"{username_raw}'s boba count is {count}"
            await message.channel.send(my_message)
        elif word_list[-1] == "info":
            my_message = "https://github.com/milo-ucla/BobaBot/blob/4f25e9e1472c81d0dcc14efe334f653d9a738e41/README.md"
            await message.channel.send(my_message)
        elif len(word_list) == 2:
            incr = 0
            my_message = "Error: unhandled exception"
            try:
                incr = int(word_list[-1])
                count = update_count(username, incr)
                my_message = f"{username_raw}'s boba count is now {count}"
            except:
                my_message = "Error: second arg invalid. Try `!boba help` for more information."
            # user just calls !boba to increment count
            await message.channel.send(my_message)
        elif len(word_list) == 1:
            # user just calls !boba to increment count
            count = update_count(username)
            my_message = f"{username_raw}'s boba count is now {count}"
            await message.channel.send(my_message)
client.run(os.getenv('TOKEN'))
