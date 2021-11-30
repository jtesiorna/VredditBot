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
    activityname = "Ye mum."
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=activityname))

@client.event
async def on_message(message):
    numgen = str(uuid.uuid4())
    if message.author.id == client.user.id:
        return
    discord_message = message.content
    tc_ss = "thanks chet"
    tc = discord_message.lower()
    reg_match = get_pattern

#-------------------------------------------------------------------------------
# Main code block for getting the v.redd.it video, downloading, compressing, etc.
    if reg_match:
        raw_reg_url = 'https://www.reddit.com/r/' + reg_match.group(2)
        url_address = raw_reg_url + '.json'
        headers = {'User-Agent': 'vredit_bot/v0.1'}
        raw_json = requests.get(url_address, headers=headers).json()
        json_parsed = json.dumps(raw_json)
        json_data = json.loads(json_parsed)


        vreddit_url = json_data[0]['data']['children'][0]['data']['url']
        post_title = json_data[0]['data']['children'][0]['data']['title']
        nsfw_tag = json_data[0]['data']['children'][0]['data']['over_18']
        raw_video_name = "vredditvid_" + numgen + ".mp4"
        compressed_video_name = "vredditcompress_" + numgen + ".mp4"

        if json_data[0]['data']['children'][0]['data']['over_18']:
            raw_video_name = "SPOLIER_" + raw_video_name
            compressed_video_name = "SPOILER_" + compressed_video_name

        #if vreddit.url.startswith = query sqlite database
        #elif do the stuff below
        if vreddit_url.startswith('https://v.redd.it'):
            ydl_opts = {'outtmpl':raw_video_name}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([vreddit_url])

            vreddit_size = os.path.getsize('/mnt/d/Documents/Bot/' + raw_video_name)
            if vreddit_size >= 8388608:
                compress_video('input.mp4', 'output.mp4', 50 * 1000, numgen)
                file = discord.File(r'/mnt/d/Documents/Bot/' + compressed_video_name)
                sender = message.author
                await message.reply(file=file, content="**Hey! I saw that you posted a Reddit-hosted video.** \nYou can stay and watch it here instead, but here are the post comments: \n" + "Title: **" + post_title + "**" +"\n<" + "vreddit_url (get rid of quotes on prod)" +">", mention_author = False)
                os.remove(compressed_video_name)

            else:
                file = discord.File(r'/mnt/d/Documents/Bot/' + raw_video_name)
                sender = message.author
                await message.reply(file=file, content="**Hey! I saw that you posted a Reddit-hosted video.** \nYou can stay and watch it here instead, but here are the post comments: \n" + "Title: **" + post_title + "**" +"\n<" + "raw_vreddit_url(get rid of quotes on prod)" + ">", mention_author = False)
                #add vreddit_url and discord link to table
                discordapp_url = '1'
                # db_connect(db_path=DEFAULT_PATH).execute("insert into contacts (name, phone, email) values (?, ?, ?)",(vreddit_url,discordapp_url))
            cleanup_files(raw_video_name, compressed_video_name)
        else:
            return

#-------------------------------------------------------------------------------
    elif tc_ss in tc:
        message_author_id = message.author.id
        treply = thankreply(message_author_id)
        await message.reply(content=treply, mention_author = False)

    #specifically for personal server. If you're using this code, you can remove this elif statement.
    elif "chet?" in tc:
        await message.reply(content="<:chetstare:880848415792173117>", mention_author= False)

    else:
        return



def cleanup_files(raw, compressed):
    os.remove(raw)
    os.remove(compressed)
    os.remove('ffmpeg2pass-0.log')
    os.remove('ffmpeg2pass-0.log.mbtree')

def get_pattern(raw):
    link_pattern = '(https://[old|new|www|v]+\.[reddit|redd]+\.[com|it]+[\w.,@^=%&:/~+#-]*[\w@^=%&/~+#-])?'
    reg_pattern = 'https://(old\.|new\.|www\.)?reddit\.com/r/([\w.,@^=%&:/~+#-]*[\w@^=%&/~+#-])?'
    link = re.search(link_pattern, discord_message)

    if link:
        return re.search(reg_pattern, requests.head(link.group(1), allow_redirects = True).url)

def db_connect(db_path=DEFAULT_PATH):
    con = sqlite3.connect(db_path)
    return con

if __name__ == '__main__':
  main(len(argv), argv)
