#import Disocrd Package
import discord

#Client (our bot)
client = discord.Client()

@client.event
async def on_ready():
    #DO STUFF...
    dev_channel = client.get_channel(564326006903537679)
    #await dev_channel.send('heehoo meatpog.')

#Run the client on the server
client.run('ODQ1NTI2MTk2MTQ0OTYzNTg0.YKiPog.Iywr1Ta_xkaHeEDlIkaWvdAJXvY')