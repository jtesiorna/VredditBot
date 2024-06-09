from __future__ import unicode_literals

import json
import os
import random
import re
import sqlite3
import sys
import urllib
import uuid
from pathlib import Path
from sys import argv
from urllib.request import urlopen

import discord
import ffmpeg
import requests
import yaml
import yt_dlp
from compressvideo import compress_video
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "database.discordurl")
video_directory = "/tmp/downloads/"

REPLIES_MAP: dict[str, list[str]] = {}
REPLIES_DEFAULT_KEY = "default"


def _addReply(key: str, message: str):

    if REPLIES_MAP.get(key, None) is None:
        REPLIES_MAP[key] = []

    REPLIES_MAP[key].append(message)


def populateReplies():

    filePath = Path("./replies.yaml")

    if not filePath.exists():
        print(
            f"WARNING: {filePath.resolve()} could not be found! Continuing with no replies loaded...",
            file=sys.stderr,
        )
        REPLIES_MAP[REPLIES_DEFAULT_KEY] = ["🤏 😑 welcome"]
        return

    replies = yaml.safe_load(filePath.read_text())

    for reply in replies:
        filter = reply.get("filter", None)

        if filter is not None and len(filter) >= 1:
            for user in filter:
                _addReply(user, reply["message"])
        else:
            _addReply(REPLIES_DEFAULT_KEY, reply["message"])


def main(argc, argv):
    populateReplies()
    # Private information:
    clientToken = os.environ.get("CHETBOT__CLIENT_TOKEN")
    # Run the client on the server
    client.run(clientToken)


def thankreply(author_id: str) -> str:

    key = REPLIES_DEFAULT_KEY

    if REPLIES_MAP.get(str(author_id), None) is not None:
        key = str(author_id)

    replies = REPLIES_MAP[key]

    if len(replies) == 0:
        return "🤏 😑 welcome"

    return random.choice(replies)


@client.event
async def on_ready():
    print("Yep. It's working.")
    activityname = "Under new management."
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.playing, name=activityname)
    )


@client.event
async def on_message(message):
    numgen = str(uuid.uuid4())
    if message.author.id == client.user.id:
        return
    discord_message = message.content
    tc_ss = "thanks chet"
    tc = discord_message.lower()
    reg_match = get_pattern(discord_message)

    # Main code block for getting the v.redd.it video, downloading, compressing, etc.

    if reg_match:
        raw_reg_url = "https://www.reddit.com/r/" + reg_match.group(2)
        url_address = raw_reg_url + ".json"
        headers = {"User-Agent": "vreddit_bot/v0.1"}
        raw_json = requests.get(url_address, headers=headers).json()
        json_parsed = json.dumps(raw_json)
        json_data = json.loads(json_parsed)

        vreddit_url = json_data[0]["data"]["children"][0]["data"]["url"]
        post_title = json_data[0]["data"]["children"][0]["data"]["title"]
        nsfw_tag = json_data[0]["data"]["children"][0]["data"]["over_18"]
        raw_video_name = "vredditvid_" + numgen + ".mp4"
        compressed_video_name = "vredditcompress_" + numgen + ".mp4"

        if json_data[0]["data"]["children"][0]["data"]["over_18"]:
            raw_video_name = "SPOILER_" + raw_video_name
            compressed_video_name = "SPOILER_" + compressed_video_name

        # if vreddit.url.startswith = query sqlite database
        # elif do the stuff below
        if vreddit_url.startswith("https://v.redd.it"):
            ydl_opts = {"outtmpl": video_directory + raw_video_name}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([vreddit_url])

            vreddit_size = os.path.getsize(video_directory + raw_video_name)
            if vreddit_size >= 8388608:
                # compress_video('input.mp4', 'output.mp4', 50 * 1000, numgen)
                compress_video(
                    video_directory + raw_video_name,
                    compressed_video_name,
                    50 * 1000,
                    numgen,
                )
                file = discord.File(video_directory + compressed_video_name)
                sender = message.author
                await message.reply(
                    file=file,
                    content="**Hey! I saw that you posted a Reddit-hosted video.** \nYou can stay and watch it here instead, but here are the post comments: \n"
                    + "Title: **"
                    + post_title
                    + "**"
                    + "\n<"
                    + vreddit_url
                    + ">",
                    mention_author=False,
                )
                # os.remove(compressed_video_name)

            else:
                file = discord.File(video_directory + raw_video_name)
                sender = message.author
                await message.reply(
                    file=file,
                    content="**Hey! I saw that you posted a Reddit-hosted video.** \nYou can stay and watch it here instead, but here are the post comments: \n"
                    + "Title: **"
                    + post_title
                    + "**"
                    + "\n<"
                    + vreddit_url
                    + ">",
                    mention_author=False,
                )
                # add vreddit_url and discord link to table
                discordapp_url = "1"
                # db_connect(db_path=DEFAULT_PATH).execute("insert into contacts (name, phone, email) values (?, ?, ?)",(vreddit_url,discordapp_url))
            cleanup_files(video_directory, raw_video_name, compressed_video_name)
        else:
            return

    elif tc_ss in tc:
        message_author_id = message.author.id
        reply = thankreply(message_author_id)
        await message.reply(content=reply, mention_author=False)

    # specifically for personal server. If you're using this code, you can remove this elif statement.
    elif "chet?" in tc:
        await message.reply(
            content="<:chetstare:880848415792173117>", mention_author=False
        )

    else:
        return


def cleanup_files(video_directory, raw, compressed):
    video_directory_path = Path(video_directory)

    (video_directory_path / raw).unlink(missing_ok=True)
    (video_directory_path / compressed).unlink(missing_ok=True)
    (video_directory_path / "ffmpeg2pass-0.log").unlink(missing_ok=True)
    (video_directory_path / "ffmpeg2pass-0.log.mbtree").unlink(missing_ok=True)


def get_pattern(raw):
    link_pattern = "(https:\/\/[old|new|www|v]+\.[reddit|redd]+\.[com|it]+[\w.,@^=%&:/~+#-]*[\w@^=%&/~+#-])+"
    reg_pattern = (
        "https://(old\.|new\.|www\.)?reddit\.com/r/([\w.,@^=%&:/~+#-]*[\w@^=%&/~+#-])?"
    )
    link = re.search(link_pattern, raw)

    if link:
        print("Homogenised URL: {}".format(link.group(1)))
        return re.search(
            reg_pattern, requests.head(link.group(1), allow_redirects=True).url
        )


def db_connect(db_path=DEFAULT_PATH):
    con = sqlite3.connect(db_path)
    return con


if __name__ == "__main__":
    main(len(argv), argv)
