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
from chatviewmodule import ChatViewModule

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
    
    @commands.group(name='youtube')
    async def youtube_cog(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Error: missing option')

    @youtube_cog.command(name='getinfo')
    async def get_videoinfo(self, ctx, *args, **kwargs):
        if len(args) == 0:
            await ctx.send('Error: need URLs!')
            return

        for url in args:
            with youtube_dl.YoutubeDL() as ydl:
                info = ydl.extract_info(url, download=False)
            print(info)
            await ctx.send(info)

    @get_videoinfo.error
    async def get_videoinfo_error(self, ctx, error):
        print(error)
        await ctx.invoke(self.bot.get_command('send_error_log'), error)

    @youtube_cog.command(name='liveinfo')
    async def get_liveinfo(seld, ctx, *args, **kwargs):
        if len(args) == 0:
            await ctx.send('Error: need URLs!')
            return

        for index, url in enumerate(args):
            info = self.ytd_info(url)
            # print(info)
            await ctx.send(info)

    @get_liveinfo.error
    async def get_liveinfo_error(self, ctx, error):
        print(error)
        await ctx.invoke(self.bot.get_command('send_error_log'), error)

    @youtube_cog.command(name='download')
    async def download_video(self, ctx, *args, **kwargs):
        url = args[0]

        ytm = YoutubeModule()

        fn = partial(ytm.data_check, url=url, ydl_ops={})
        try:
            text = await self.bot.loop.run_in_executor(None, fn)
        except Exception as e:
            await ctx.invoke(self.bot.get_command('send_error_log'), error)
            raise e

        print(text)
        await ctx.send(text)

        fn = partial(ytm.download_video, url=url)
        try:
            result = await self.bot.loop.run_in_executor(None, fn)
        except Exception as e:
            await ctx.invoke(self.bot.get_command('send_error_log'), error)
            raise e
        info = result[0]
        outpath = result[1]
        title = result[2]
        date = result[3]
        pool = result[4]
        print('Download Success!')
        try:
            await ctx.invoke(self.bot.get_command('send_output_log'), info=info, url=url)
        except Exception as e:
            await ctx.invoke(self.bot.get_command('send_error_log'), error)
            raise e

        '''
        if '%(is_live)s' % info != 'True':
            fn = partial(os.remove, outpath)
            try:
                info = await self.bot.loop.run_in_executor(None, fn)
            except Exception as e:
                await ctx.invoke(self.bot.get_command('send_error_log'), e)
                raise e
            return
        #'''

        await pool.wait()
        cvm = ChatViewModule(ytm.get_videoid(url=url))
        fn = partial(cvm.cut_movie, file_path=outpath, title=title, date=date)
        try:
            info = await self.bot.loop.run_in_executor(None, fn)
        except Exception as e:
            await ctx.invoke(self.bot.get_command('send_error_log'), e)
            raise e

        return

    @download_video.error
    async def download_video_error(self, ctx, error):
        print(error)
        await ctx.invoke(self.bot.get_command('send_error_log'), error)

def setup(bot):
    return bot.add_cog(YoutubeCog(bot))
