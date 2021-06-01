#PACKAGES/IMPORTS
from __future__ import unicode_literals
import discord, requests, json, uuid, os, re, ffmpeg, youtube_dl
from urllib.request import urlopen
from discord.ext import commands

#-----------------------------------------------------------------------------
#Client (the bot)
client = discord.Client()
#private information:
with open('clientToken.txt','r') as cl_token:
    clienttoken = cl_token.read()

def cleanup_files(numgen):
    os.remove('vredditvid_' + numgen + '.mp4')
    os.remove('ffmpeg2pass-0.log')
    os.remove('ffmpeg2pass-0.log.mbtree')

#EVENTS:
@client.event
async def on_message(message):
    numgen = str(uuid.uuid4())
    if message.author.id == client.user.id:
        return
    reg_pattern = 'https://(old\.|new\.|www\.)?reddit\.com/r/([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?'
    vreddit_pattern = 'https://v\.redd\.it/([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?'
    discord_message = message.content
    reg_match = re.search(reg_pattern, discord_message)
    vreddit_match = re.search(vreddit_pattern, discord_message)

    if reg_match:
        url_address = message.content + '.json'
        headers = {'User-Agent': 'vredit_bot/v0.1'}
        raw_json = requests.get(url_address, headers=headers).json()
        json_parsed = json.dumps(raw_json)
        json_data = json.loads(json_parsed)


        vreddit_url = json_data[0]['data']['children'][0]['data']['url']
        if vreddit_url.startswith('https://v.redd.it'):
            ydl_opts = {'outtmpl':'vredditvid_' + numgen + '.mp4'}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([vreddit_url])

            vreddit_size = os.path.getsize('/mnt/d/Documents/Bot/vredditvid_' + numgen + '.mp4')
            if vreddit_size >= 8388608:
                compress_video('input.mp4', 'output.mp4', 50 * 1000, numgen)
                file = discord.File(r'/mnt/d/Documents/Bot/vredditcompress_' + numgen + '.mp4')
                sender = message.author
                await message.reply(file=file, content="**Hey! I saw that you posted a Reddit-hosted video.** \nYou can stay and watch it here instead, but here's a direct link to the post comments: "+"<"+vreddit_url+">", mention_author = False)
                os.remove('vredditcompress_' + numgen + '.mp4')

            else:
                file = discord.File(r'/mnt/d/Documents/Bot/vredditvid_' + numgen + '.mp4')
                sender = message.author
                await message.reply(file=file, content="**Hey! I saw that you posted a Reddit-hosted video.** \nYou can stay and watch it here instead, but here's a direct link to the post comments: "+"<"+vreddit_url+">", mention_author = False)
            cleanup_files(numgen)
        else:
            return

    elif vreddit_match:
        raw_vreddit_url = vreddit_match.group(0)
        ydl_opts = {'outtmpl':'vredditvid_' + numgen + '.mp4'}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([raw_vreddit_url])

        vreddit_size = os.path.getsize('/mnt/d/Documents/Bot/vredditvid_' + numgen + '.mp4')
        if vreddit_size >= 8388608:
            compress_video('input.mp4', 'output.mp4', 50 * 1000, numgen)

            file = discord.File(r'/mnt/d/Documents/Bot/vredditcompress_' + numgen + '.mp4')
            sender = message.author
            await message.reply(file=file, content="**Hey! I saw that you posted a Reddit-hosted video.** \nYou can stay and watch it here instead, but here's a direct link to the post comments: "+"<"+raw_vreddit_url+">", mention_author = False)
            os.remove('vredditcompress_' + numgen + '.mp4')
        else:
            file = discord.File(r'/mnt/d/Documents/Bot/vredditvid_' + numgen + '.mp4')
            sender = message.author
            await message.reply(file=file, content="**Hey! I saw that you posted a Reddit-hosted video.** \nYou can stay and watch it here instead, but here's a direct link to the post comments: "+"<"+raw_vreddit_url+">", mention_author = False)
        cleanup_files(numgen)
    else:
        return
#Run the client on the server
client.run(clienttoken)




#THIS CODE TAKEN FROM: https://stackoverflow.com/questions/64430805/how-to-compress-video-to-target-size-by-python
def compress_video(video_full_path, output_file_name, target_size, numgen):
    video_full_path = '/mnt/d/Documents/Bot/vredditvid_' + numgen + '.mp4'
    output_file_name = 'vredditcompress_' + numgen + '.mp4'
    target_size = 8000
    min_audio_bitrate = 32000
    max_audio_bitrate = 256000
    probe = None
    try:
        probe = ffmpeg.probe(video_full_path)
    except ffmpeg.Error as e:
        print(e.stderr)
        exit()
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
