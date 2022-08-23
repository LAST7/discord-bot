#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File     :   main.py
@Time     :   2022/08/20 23:47:04
@Author   :   Last
@Version  :   1.0
@Contact  :   lustrously_@outlook.com
@Software :   Microsoft_VS_Code
'''


import discord
import asyncio
import youtube_dl


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# greb token from the txt file
with open('./bot_token.txt') as bot_token:
    token = bot_token.readline()

block_words = ['genshin', 'genshit']


# part for music playing
voice_clients = {}

yt_dl_opts = {'format': 'bestaudio/best'}
ytdl = youtube_dl.YoutubeDL(yt_dl_opts)

ffmpeg_opts = {'options': '-vn'}


@client.event
async def on_ready():
    print('Bot is now online and ready.')


@client.event
async def on_message(msg):

    # blocked words section
    #######################
    if msg.author != client.user:
        for text in block_words:
            if text in str(msg.content.lower()):
                print(f'blocked word "{text}" detected')

                # * 'genshin'
                if text == 'genshin' or 'genshit':
                    await msg.delete()
                    await msg.channel.send('No Genshit in this server!')
                    print('genshit deleted.')
                    return

    #######################

    # help
    #######################
    if msg.content.startswith('.help'):
        await msg.channel.send(file=discord.File('./discord bot help.png'))
        print('help picture sent.')

    # audio section
    #######################
    # * ?play
    if msg.content.startswith('?play'):
        # check the legality of the url
        url = msg.content.split()[1]
        if 'www.youtube.com' not in url:
            await msg.channel.send('Illegal url, please use a Youtube url.')
            print('Illegal url, process stopped.')
            return

        try:
            # Let the bot connect to the voice channel of the user(msg.author)
            voice_client = await msg.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client

        except discord.errors.ClientException:
            # if a new audio is provided when bot is already connected to voice channel.
            voice_clients[msg.guild.id].pause()
            await msg.channel.send(f'Currently playing audio stopped, playing new audio provided by {msg.author}')
            print(f'Currently playing audio stopped by {msg.author}, playing new audio.')

        except AttributeError:
            await msg.channel.send(f'User {msg.author} not in any voice channel. Please join in a voice channel for the bot to play audio.')
            print(f'User {msg.author} not in voice channel, process stopped.')
            return

        try:
            # Download the audio file of the youtube video provided by the user
            await msg.channel.send(f'Downloading audio provided by {msg.author}.')
            loop = asyncio.get_event_loop()
            audio_data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

            # Store the audio data and start ffmpeg to stream(?)
            song = audio_data['url']
            player = discord.FFmpegPCMAudio(song, **ffmpeg_opts)

            # Start playing audio
            await msg.channel.send(f'Playing audio provided by {msg.author}')
            voice_clients[msg.guild.id].play(player)

        except Exception as err:
            await msg.channel.send('Unable to play audio.')
            await msg.channel.send(f'err: {err}')
            print(err)

    # * ?pause
    if msg.content.startswith('?pause'):
        try:
            voice_clients[msg.guild.id].pause()

            await msg.channel.send(f'Audio paused by {msg.author}')
            print(f'Audio paused by {msg.author}.')

        except Exception as err:
            await msg.channel.send('Unable to pause audio')
            await msg.channel.send(f'err: {err}')
            print(err)

    # * ?resume
    if msg.content.startswith('?resume'):
        try:
            voice_clients[msg.guild.id].resume()

            await msg.channel.send(f'Audio resumed by {msg.author}')
            print(f'Audio resumed by {msg.author}.')

        except Exception as err:
            await msg.channel.send('Unable to resume audio')
            await msg.channel.send(f'err: {err}')
            print(err)

    # * ?stop
    if msg.content.startswith('?stop'):
        try:
            voice_clients[msg.guild.id].stop()

            # disconnect the bot from the voice channel
            await voice_clients[msg.guild.id].disconnect()

            await msg.channel.send(f'Audio stopped by {msg.author}, bot disconnected from the voice channel.')
            print(f'Audio stopped by {msg.author}. Bot disconnected from voice channel.')

        except Exception as err:
            await msg.channel.send('Unable to stop audio')
            await msg.channel.send(f'err: {err}')
            print(err)

    #######################


client.run(token)
