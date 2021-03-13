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
import shutil
import importlib
from multiprocessing import Pool

import discord
from discord.ext import commands
import youtube_dl

import db_connect
import youtubemodule
import chatdatamodule
import youtubeapi
import property


class YoutubeCog(commands.Cog):
    def __init__(self, bot):
        importlib.reload(importlib)
        importlib.reload(db_connect)
        importlib.reload(youtubemodule)
        importlib.reload(chatdatamodule)
        importlib.reload(youtubeapi)
        importlib.reload(property)
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

    @staticmethod
    def parse_url(url):
        try:
            url = requests.get(url).url.split('&')[0]
            # parsed_url = urllib.parse.urlparse(url)
            return url
        except Exception as e:
            raise e
    
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
        # url = args[0]
        url = self.parse_url(args[0])

        ytm = youtubemodule.YoutubeModule()

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
            info = await self.bot.loop.run_in_executor(None, fn)
        except Exception as e:
            await ctx.invoke(self.bot.get_command('send_error_log'), e)
            raise e
        print('Download Success!')
        try:
            await ctx.invoke(self.bot.get_command('send_video_output_log'), info=info, url=url)
        except Exception as e:
            await ctx.invoke(self.bot.get_command('send_error_log'), e)
            raise e
        return

        #コメント処理
        '''
        cvm = chatviewmodule.ChatViewModule(ytm.get_videoid(url=url), date)
        fn = partial(cvm.cut_movie, file_path=outpath, title=title, date=date, pool=pool)
        try:
            info = await self.bot.loop.run_in_executor(None, fn)
        except Exception as e:
            await ctx.invoke(self.bot.get_command('send_error_log'), e)
            raise e
        '''

        return

    @download_video.error
    async def download_video_error(self, ctx, error):
        print(error)
        await ctx.invoke(self.bot.get_command('send_error_log'), error)

    @youtube_cog.command(name='highlight')
    async def get_highlight(self, ctx, *args, **kwargs):
        # url = args[0]
        url = self.parse_url(args[0])

        await ctx.send('Starting get highlight...')

        ytm = youtubemodule.YoutubeModule()
        video_id = ytm.get_videoid(url=url)

        ytapi = youtubeapi.YoutubeApi()
        try:
            livedetail = ytapi.get_livedetail(video_id)
        except Exception as e:
            await ctx.invoke(self.bot.get_command('send_error_log'), e)
            raise e
        cdm = chatdatamodule.ChatDataModule(video_id=video_id, url=url, livedetail=livedetail)
        '''
        pool = Pool(1)
        try:
            result = pool.apply_async(cdm.get_highlight)
            result.wait()
            highlight_urls = result.get()
        except Exception as e:
            await ctx.invoke(self.bot.get_command('send_error_log'), e)
        '''

        fn = partial(cdm.get_highlight)
        try:
            highlight_urls = await self.bot.loop.run_in_executor(None, fn)
        except Exception as e:
            await ctx.invoke(self.bot.get_command('send_error_log'), e)
            raise e

        # print(len(highlight_url))
        # res = '\n'.join(highlight_url)
        # await ctx.invoke(self.bot.get_command('echo'), res)

        try:
            channel_name = ytapi.get_channel_name(livedetail)
            title = ytapi.get_title(livedetail)
            thumbnail_url = ytapi.get_thumbnail_url(livedetail)

            graph_image = cdm.image_path
            print(graph_image)
            file = discord.File(graph_image, filename='image.png')

            embed = discord.Embed(title=title, description=channel_name, color=0xff0000)
            embed.set_thumbnail(url=thumbnail_url)
            highlight_url_text = ''
            for highlight in highlight_urls:
                tmp = highlight_url_text + str(datetime.timedelta(seconds=highlight[0])) + '\t' + highlight[1] + '\n'
                if len(tmp) < 1024:
                    highlight_url_text = tmp
                else:
                    embed.add_field(name="highlight",value=highlight_url_text)
                    highlight_url_text = ''
            if highlight_url_text != '':
                embed.add_field(name="highlight",value=highlight_url_text)
            else:
                embed.add_field(name="highlight",value="does not get highlight")
            embed.set_image(url="attachment://image.png")

            await ctx.invoke(self.bot.get_command('send_highlight_output_log'), file, embed)
        except Exception as e:
            await ctx.invoke(self.bot.get_command('send_error_log'), e)
            raise e

        try:
            out_path = "/mnt/media/Youtube/graphImage/"
            if not os.path.exists(out_path):
                os.mkdir(out_path)
            shutil.move(graph_image, out_path)
        except Exception as e:
            await ctx.invoke(self.bot.get_command('send_error_log'), e)
            raise e
        return

def setup(bot):
    return bot.add_cog(YoutubeCog(bot))
