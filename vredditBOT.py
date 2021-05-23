#PACKAGES/IMPORTS
from __future__ import unicode_literals
import discord
import urllib, requests
import json
import uuid
import os, ffmpeg
import youtube_dl
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
    if message.author.id == client.user.id:
        return
#--------------------------------------------
#LOOKS FOR AND GRABS V.REDD.IT LINK AND DOWNLOADS IT
    if message.content.startswith('https://www.reddit.com',0,22):
        url_address = message.content + '.json'
        headers = {'User-Agent': 'vredit_bot/v0.1'}
        x = requests.get(url_address, headers=headers).json()
        y = json.dumps(x)
        z = json.loads(y)

        vreddit_url = z[0]['data']['children'][0]['data']['url']
        if vreddit_url.startswith('https://v.redd.it'):
            ydl_opts = {'outtmpl':'vredditvid'}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([vreddit_url])
#--------------------------------------------
#COMPRESS VIDEO TO <8MB
            #THIS CODE TAKEN FROM: https://stackoverflow.com/questions/64430805/how-to-compress-video-to-target-size-by-python
            def compress_video(video_full_path, output_file_name, target_size):

                video_full_path = '/mnt/d/Documents/Bot/vredditvid.mp4'
                output_file_name = 'vredditcompress.mp4'
                target_size = 8000
                min_audio_bitrate = 32000
                max_audio_bitrate = 256000

                probe = ffmpeg.probe(video_full_path)
                # Video duration, in s.
                duration = float(probe['format']['duration'])
                # Audio bitrate, in bps.
                audio_bitrate = float(next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)['bit_rate'])

                # Target total bitrate, in bps.
                target_total_bitrate = (target_size * 1024 * 8) / (1.073741824 * duration)

                # Target audio bitrate, in bps
                if 10 * audio_bitrate > target_total_bitrate:
                    audio_bitrate = target_total_bitrate / 10
                    if audio_bitrate < min_audio_bitrate < target_total_bitrate:
                        audio_bitrate = min_audio_bitrate
                    elif audio_bitrate > max_audio_bitrate:
                        audio_bitrate = max_audio_bitrate
                # Target video bitrate, in bps.
                video_bitrate = target_total_bitrate - audio_bitrate

                i = ffmpeg.input(video_full_path)
                ffmpeg.output(i, os.devnull,
                              **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}
                              ).overwrite_output().run()
                ffmpeg.output(i, output_file_name,
                              **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac', 'b:a': audio_bitrate}
                              ).overwrite_output().run()
            compress_video('input.mp4', 'output.mp4', 50 * 1000)
#--------------------------------------------
#DELETE ORIGINAL LINK AND SEND VIDEO ON DISCORD CHANNEL
            file = discord.File(r'/mnt/d/Documents/Bot/vredditcompress.mp4')
            sender = message.author
            await message.reply(file=file, content="**Hey! I saw that you posted a Reddit-hosted video.** \nYou can stay and watch it here instead, but here's a link to the post comments: "+"<"+vreddit_url+">", mention_author = False)

#--------------------------------------------
#CLEANUP DIRECTORY
            os.remove('vredditcompress.mp4')
            os.remove('vredditvid.mp4')
            os.remove('ffmpeg2pass-0.log')
            os.remove('ffmpeg2pass-0.log.mbtree')

        else:
            return


#Run the client on the server
client.run(clienttoken)
