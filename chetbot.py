#PACKAGES/IMPORTS
from __future__ import unicode_literals
import discord, requests, json, uuid, os, re, ffmpeg, yt_dlp, urllib, sqlite3
from urllib.request import urlopen
from discord.ext import commands
from sys import argv
import random
from thankreplies import thankreply
from compressvideo import compress_video

#-----------------------------------------------------------------------------
#Global variables
client = discord.Client()
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.discordurl')

def main(argc, argv):
    #Private information:
    with open('clientToken.txt','r') as cl_token:
        clienttoken = cl_token.read()
    #Run the client on the server
    client.run(clienttoken)

#EVENTS:
@client.event
async def on_ready():
    print("Yep. It's working.")
    activityname = "Reddit videos!"
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=activityname))

@client.event
async def on_message(message):
    numgen = str(uuid.uuid4())
    if message.author.id == client.user.id:
        return
    reg_pattern = 'https://(old\.|new\.|www\.)?reddit\.com/r/([\w.,@^=%&:/~+#-]*[\w@^=%&/~+#-])?'
    vreddit_pattern = 'https://v\.redd\.it/([\w.,@^=%&:/~+#-]*[\w@^=%&/~+#-])?'
    discord_message = message.content
    tc_ss = "thanks chet"
    tc = discord_message.lower()
    reg_match = re.search(reg_pattern, discord_message)
    vreddit_match = re.search(vreddit_pattern, discord_message)



    if reg_match:
        raw_reg_url = 'https://www.reddit.com/r/' + reg_match.group(2)
        url_address = raw_reg_url + '.json'
        headers = {'User-Agent': 'vredit_bot/v0.1'}
        raw_json = requests.get(url_address, headers=headers).json()
        json_parsed = json.dumps(raw_json)
        json_data = json.loads(json_parsed)


        vreddit_url = json_data[0]['data']['children'][0]['data']['url']
        post_title = json_data[0]['data']['children'][0]['data']['title']

        #if vreddit.url.startswith = query sqlite database
        #elif do the stuff below
        if vreddit_url.startswith('https://v.redd.it'):
            ydl_opts = {'outtmpl':'vredditvid_' + numgen + '.mp4'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([vreddit_url])

            vreddit_size = os.path.getsize('/mnt/d/Documents/Bot/vredditvid_' + numgen + '.mp4')
            if vreddit_size >= 8388608:
                compress_video('input.mp4', 'output.mp4', 50 * 1000, numgen)
                file = discord.File(r'/mnt/d/Documents/Bot/vredditcompress_' + numgen + '.mp4')
                sender = message.author
                await message.reply(file=file, content="**Hey! I saw that you posted a Reddit-hosted video.** \nYou can stay and watch it here instead, but here are the post comments: \n" + "Title: **" + post_title + "**" +"\n<" + "vreddit_url (get rid of quotes on prod)" +">", mention_author = False)
                os.remove('vredditcompress_' + numgen + '.mp4')

            else:
                file = discord.File(r'/mnt/d/Documents/Bot/vredditvid_' + numgen + '.mp4')
                sender = message.author
                await message.reply(file=file, content="**Hey! I saw that you posted a Reddit-hosted video.** \nYou can stay and watch it here instead, but here are the post comments: \n" + "Title: **" + post_title + "**" +"\n<" + "vreddit_url(get rid of quotes on prod)" + ">", mention_author = False)
                #add vreddit_url and discord link to table
                discordapp_url = '1'
                db_connect(db_path=DEFAULT_PATH).execute("insert into contacts (name, phone, email) values (?, ?, ?)",(vreddit_url,discordapp_url))
            cleanup_files(numgen)
        else:
            return

    elif tc_ss in tc:
        treply = thankreply()
        await message.reply(content=treply, mention_author = False)

    elif vreddit_match:
        raw_vreddit_url = vreddit_match.group(0)
        ydl_opts = {'outtmpl':'vredditvid_' + numgen + '.mp4'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([raw_vreddit_url])

        vreddit_size = os.path.getsize('/mnt/d/Documents/Bot/vredditvid_' + numgen + '.mp4')
        if vreddit_size >= 8388608:
            compress_video('input.mp4', 'output.mp4', 50 * 1000, numgen)

            file = discord.File(r'/mnt/d/Documents/Bot/vredditcompress_' + numgen + '.mp4')
            sender = message.author
            await message.reply(file=file, content="**Hey! I saw that you posted a Reddit-hosted video.** \nYou can stay and watch it here instead, but here are the post comments: \n" + "<" + "raw_vreddit_url(get rid of quotes on prod)" + ">", mention_author = False)
            os.remove('vredditcompress_' + numgen + '.mp4')
        else:
            file = discord.File(r'/mnt/d/Documents/Bot/vredditvid_' + numgen + '.mp4')
            sender = message.author
            await message.reply(file=file, content="**Hey! I saw that you posted a Reddit-hosted video.** \nYou can stay and watch it here instead, but here are the post comments: \n" + "<" + "raw_vreddit_url(get rid of quotes on prod)" + ">", mention_author = False)
        cleanup_files(numgen)

    else:
        return



def cleanup_files(numgen):
    os.remove('vredditvid_' + numgen + '.mp4')
    os.remove('ffmpeg2pass-0.log')
    os.remove('ffmpeg2pass-0.log.mbtree')



def db_connect(db_path=DEFAULT_PATH):
    con = sqlite3.connect(db_path)
    return con

if __name__ == '__main__':
  main(len(argv), argv)
