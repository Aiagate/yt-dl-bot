#! /usr/bin/env python3
import asyncio
import discord
import requests
import urllib

from discord.ext import commands
import property

class MainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener(name='on_message')
    async def on_message(self, message):

        #Bot同士による会話を制限
        if message.author.bot:
            return
        #コマンドの場合処理をしない
        if '!' in message.content:
            return

        #URLを展開
        try:
            url = requests.get(message.content).url.split('&')[0]
            parsed_url = urllib.parse.urlparse(url)
            message.content = '!urlparse ' + url
            await self.bot.process_commands(message)

        except Exception as e:
            # raise e
            return

        return

    @commands.command(name='urlparse')
    async def urlparse(self, ctx, *args, **kwargs):
        #URLを展開
        try:
            url = requests.get(args[0]).url.split('&')[0]
            parsed_url = urllib.parse.urlparse(url)
        except Exception as e:
            raise e

        #YoutubeのURLの場合処理を続行
        if parsed_url.netloc == 'www.youtube.com':
            await ctx.invoke(self.bot.get_command('youtube download'), url)

def setup(bot):
    return bot.add_cog(MainCog(bot))