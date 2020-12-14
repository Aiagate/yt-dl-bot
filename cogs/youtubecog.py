#! /usr/bin/env python3
import discord
from discord.ext import commands
import youtube_dl
from functools import partial
import os
import time
import shutil
import asyncio
import signal
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

    @commands.command()
    async def getinfo(self, ctx):
        args = ctx.message.content.split()

        if len(args) == 1:
            await ctx.send('Error: need URLs!')
            return

        for index, url in enumerate(args):
            if index != 0:
                self.info = self.ytd_info(url)
                # print(info)
                await ctx.send(info)

    @getinfo.error
    async def getinfo_error(self, ctx, error):
        print(error)
        await ctx.send('Error: ' + str(error))

    @commands.Cog.listener(name='on_message')
    async def get_url(self, message,):
        if message.author.bot:
            return
        if message.content.startswith('http'):
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
            shutil.move(file_path % data, '/mnt/media/Youtube/' + title + '.%(ext)s' % data)
            await self.bot.get_channel(property.OUTPUT_CHANNEL).send(' Success: ' + title + '.%(ext)s' % data)
        else:
            return


def setup(bot):
    return bot.add_cog(YoutubeCog(bot))
