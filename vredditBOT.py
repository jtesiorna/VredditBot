#Discord Package
import discord

#Client (our bot)
client = discord.Client()

#ch_token = open('channeltoken.txt','r')
#channeltoken = ch_token.readline()
cl_token = open('clientToken.txt','r')
clienttoken = cl_token.readline()

#@client.event
#async def on_ready():
#    dev_channel = client.get_channel(564326006903537679)
#    await dev_channel.send('heehoo meatpog.')

@client.event
async def on_message(message):

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

#Run the client on the server
client.run(clienttoken)
