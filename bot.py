#!/usr/bin/env python3
import discord
import os
import requests
import json
from dotenv import load_dotenv
from pymongo import MongoClient
import random
import spacy

load_dotenv()

nlp = spacy.load("en_core_web_sm")
client = discord.Client()

mongoclient = MongoClient(os.getenv("MONGO_URL"))
db = client.boba_db

boba_count = db.boba_count


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


def get_count(user):
    user_query = {
            "user": user,
    }
    query_user = boba_count.find_one(user_query)
    if query_user is None:
        return 0
    else:
        return query_user.boba_count

def update_count(user):
    # TODO: hash client.user when adding to db for privacy
    user_query = {
            "user": user,
    }
    query_user = boba_count.find_one(user_query)
    if query_user is None:
        count = 0
        user_query["boba_count"] = count
        r = boba_count.insert_one(user_query)
        print(r)
    else:
        filter = { 'user': client.user }

        newvalues = { "$set": { 'boba_count': query_user.count + 1 } }
        r = boba_count.update_one(filter, newvalues) 
        count = query_user.count + 1
        print(r)
    return count

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
        word_list = message.split(" ")
        if len(word_list) > 2:
            my_message = f"Use the boba count with 1 argument"
            await message.channel.send(my_message)
        elif word_list[:-1] == "count":
            # user calls !boba count to get their boba count
            count = get_count(message.user)
            my_message = f"{client.user}'s boba count is {count}"
            await message.channel.send(my_message)
        elif len(word_list) == 1:
            # user just calls !boba to increment count
            count = update_count(message.user)
            my_message = f"{client.user}'s boba count is now {count}"
            await message.channel.send(my_message)

client.run(os.getenv('TOKEN'))
