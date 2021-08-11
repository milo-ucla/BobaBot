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
    collection_name = db.list_collection_names()[0]
    collection = db.collection_name
    user_query = {
            "user": user,
    }
    query_user = collection.find_one(user_query)
    if query_user is None:
        return 0
    else:
        return query_user["boba_count"]


def update_count(channel, user, increment=1):
    collection = db[str(channel)]
    user_query = {
            "user": user,
    }
    query_user = collection.find_one(user_query)
    if query_user is None:
        count = increment
        user_query["boba_count"] = count
        collection.insert_one(user_query)
    else:
        filter = { 'user': user }
        newvalues = { "$set": { 'boba_count': query_user["boba_count"] + increment } }
        collection.update_one(filter, newvalues) 
        count = query_user["boba_count"] + increment
    return count


def add_user_to_server_db(user, server: str):
    collection = db[server]
    user_query = {
            "user": user,
    }
    query_user = collection.find_one(user_query)
    if query_user is None:
        collection.insert_one(user_query)


async def handle_boba(message):
    username = str(message.author).split("#")[0]
    channel = str(message.guild)

    add_user_to_server_db(username, channel)
    
    word_list = message.content.split(" ")
    if len(word_list) > 2 or word_list[-1] == "help":
        my_message = f"Use the boba count with 1 argument.\nType `count` to get your boba count, type `integer` to add to your boba count (default: 1).\nFor more information, try !boba info"
        await message.channel.send(my_message)
    elif word_list[-1] == "count":
        # user calls !boba count to get their boba count
        count = get_count(username)
        my_message = f"{username}'s boba count is {count}"
        await message.channel.send(my_message)
    elif word_list[-1] == "info":
        my_message = "https://github.com/milo-ucla/BobaBot/blob/4f25e9e1472c81d0dcc14efe334f653d9a738e41/README.md"
        await message.channel.send(my_message)
    elif len(word_list) == 2:
        incr = 0
        my_message = "Error: unhandled exception"
        try:
            incr = int(word_list[-1])
            count =  update_count(channel, username, incr)  # update_across_databases(username, incr)
            my_message = f"{username}'s boba count is now {count}"
        except:
            my_message = "Error: second arg invalid. Try `!boba help` for more information."
        # user just calls !boba to increment count
        await message.channel.send(my_message)
    elif len(word_list) == 1:
        # user just calls !boba to increment count
        count = update_count(channel, username)
        my_message = f"{username}'s boba count is now {count}"
        await message.channel.send(my_message)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    channel = message.guild

    if str(channel) not in db.list_collection_names():
        db.create_collection(str(channel))
    
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
        await handle_boba(message)


client.run(os.getenv('TOKEN'))
