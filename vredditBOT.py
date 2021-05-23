#PACKAGES/IMPORTS
import discord
import urllib, requests
import json
from urllib.request import urlopen
from discord.ext import commands

#-----------------------------------------------------------------------------
#BOT EVENTS/INFORMATION

#Client (the bot)
client = discord.Client()

#private information:
cl_token = open('clientToken.txt','r')
clienttoken = cl_token.readline()

#EVENTS:
@client.event
async def on_message(message):
#                                   V------ haven't gotten this to work yet. Supposed to ignore it's own messages
#    if message.author == self.user:
#        return
    if 'hello' in message.content:                                  #test just to make sure it works
        await message.channel.send('help me.')

    if message.content.startswith('https://www.reddit.com',0,22):
        await message.channel.send('>>>')
        url_address = message.content + '.json'
        headers = {'User-Agent': 'vredit_bot/v0.1'}
        x = requests.get(url_address, headers=headers).json()
        y = json.dumps(x)
        z = json.loads(y)

        vreddit_url = z[0]['data']['children'][0]['data']['url']
        if
        await message.channel.send(vreddit_url)


#Run the client on the server
client.run(clienttoken)
