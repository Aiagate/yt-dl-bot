#! /usr/bin/env python3

import asyncio
import datetime
from functools import partial
import os
import requests
import signal
import sqlite3
import time
import urllib

import discord
from discord.ext import commands
import youtube_dl

from db_connect import DatabaseConnect
from youtubemodule import YoutubeModule

import property


class YoutubeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def ytd_process(url, ydl_ops):
        with youtube_dl.YoutubeDL(ydl_ops) as ydl:
            data = ydl.extract_info(url, download=True)
        return data

    @staticmethod
    def ytd_info(url, ydl_ops={}):
        with youtube_dl.YoutubeDL(ydl_ops) as ydl:
            info = ydl.extract_info(url, download=False)
            return info

    @staticmethod
    def ytd_title(self, url):
        info = self.ytd_info(url)
        return ('%(title)s' % info)

    @commands.command(name='getinfo')
    async def get_videoinfo(self, ctx):
        args = ctx.message.content.split()

        if len(args) == 1:
            await ctx.send('Error: need URLs!')
            return

        for index, url in enumerate(args):
            if index != 0:
                self.info = self.ytd_info(url)
                # print(info)
                await ctx.send(info)

    @get_videoinfo.error
    async def get_videoinfo_error(self, ctx, error):
        print(error)
        await ctx.send('Error: ' + str(error))

    @commands.command(name='liveinfo')
    async def get_liveinfo(seld, ctx):
        args = ctx.message.content.split()

        if len(args) == 1:
            await ctx.send('Error: need URLs!')
            return

        for index, url in enumerate(args):
            if index != 0:
                self.info = self.ytd_info(url)
                # print(info)
                await ctx.send(info)

    @get_liveinfo.error
    async def get_liveinfo_error(self, ctx, error):
        print(error)
        await ctx.send('Error: ' + str(error))

    @commands.Cog.listener(name='on_message')
    async def video_download(self, message,):
        if message.author.bot:
            return
        
        if '!' in message.content:
            return

        try:
            url = requests.get(message.content).url.split('&')[0]
            parsed_url = urllib.parse.urlparse(url)
        except Exception as e:
            raise e

        if parsed_url.netloc == 'www.youtube.com':
            ytm = YoutubeModule()
            fn = partial(ytm.data_check, url=url, ydl_ops={})
            try:
                text = await self.bot.loop.run_in_executor(None, fn)
            except Exception as e:
                await message.channel.send('Error: ' + str(e))
                raise e

            print(text)
            await message.channel.send(text)

            fn = partial(ytm.download_video, url=url)
            try:
                info = await self.bot.loop.run_in_executor(None, fn)
            except Exception as e:
                await message.channel.send('Error: ' + str(e))
                raise e
            
            print('Success!')
            await self.bot.get_channel(property.OUTPUT_CHANNEL).send(' Success: %(title)s \n' % info + url)

            

        '''
        ng_word = {
            '\\': '＼',
            '/': '／',
            ':': '：',
            '<': '＜',
            '>': '＞',
            '|': '｜',
            '?': '？',
        }

        title = self.ytd_title(self, message.content)
        title = title.translate(str.maketrans(ng_word))
        print(title)

        outpath = os.getcwd() + '/tmp/' + '%(upload_date)s_' + title + '.%(ext)s'

        fn = partial(ydm.download_video, video_url)
        # fn = partial(ydm.download_video, video_url, ydm.ops(info, outpath)
        info=await self.bot.loop.run_in_executor(None, fn)




            file_path = os.getcwd() + '/tmp/' + '%(upload_date)s_' + title + '.%(ext)s'
            ydl_ops = {
                "outtmpl": file_path,
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mkv',
                'noplaylist': True,
                'keepvideo': False,
                'nooverwrites': True,
                'hls_use_mpegts': True,
                # 'postprocessors': [{
                # 'key': 'FFmpegFixupM4a',
                # }],
            }
            fn = partial(self.ytd_process, message.content, ydl_ops)
            data = await self.bot.loop.run_in_executor(None, fn)

            await asyncio.sleep(3)

            # await message.channel.send(file_path % data)
            # shutil.move(file_path % data, '/mnt/media/Youtube/' + '%(upload_date)s_' + title + '.%(ext)s' % data)
            # shutil.move(file_path % data, '/mnt/media/Youtube/' + title + '.%(ext)s' % data)
            shutil.move(file_path % data, '/mnt/media/Youtube/' + \
                        title + '.%(ext)s' % data)
            await self.bot.get_channel(property.OUTPUT_CHANNEL).send(' Success: ' + title + '.%(ext)s' % data)
        else:
            return
        # '''


'''
    @video_download.error
    async def video_download_error(self, ctx, error):
        print(error)
        await ctx.send('Error: ' + str(error))
'''


def setup(bot):
    return bot.add_cog(YoutubeCog(bot))
