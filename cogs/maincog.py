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

    @staticmethod
    def is_url(text):
        try:
            url = requests.get(text)
            return True
        except Exception as e:
            return False
    
    @staticmethod
    def get_domain(url):
        try:
            url = requests.get(url).url.split('&')[0]
            parsed_url = urllib.parse.urlparse(url)
            print(parsed_url.netloc)
            return parsed_url.netloc
        except Exception as e:
            raise e
    
    @commands.Cog.listener(name='on_message')
    async def on_message(self, message):
        '''
        print(message.author)
        print(type(message.author))
        print(message.author.name)
        print(message.author.discriminator)
        print(message.author.avatar)
        print(message.author.bot)
        print(message.author.display_name)
        print(message.author.mention)
        print(message.author.id)
        '''

        if message.author.id == 818670361985286165:
            for text in message.content.split(' '):
                if self.is_url(text):
                    if self.get_domain(text) == 'www.youtube.com':
                        message.content = '!echo ' + text
                        # message.content = '!highlight ' + text
                        break
        #Bot同士による会話を制限
        elif message.author.bot:
            return
        #コマンドの場合処理をしない
        elif '!' in message.content:
            return
        elif self.is_url(message.content):
            if self.get_domain(message.content) == 'www.youtube.com':
                if message.channel.id == property.HIGHLIGHT_CHANNEL:
                    message.content = '!youtube highlight ' + message.content
                elif message.channel.id == property.DOWNLOAD_CHANNEL:
                    message.content = '!youtube download ' + message.content
        else:
            return

        print(message.content)
        await self.bot.process_commands(message)
        return

        #URLを展開
        '''
        try:
            url = requests.get(message.content).url.split('&')[0]
            parsed_url = urllib.parse.urlparse(url)
            message.content = '!urlparse ' + url
        except Exception as e:
            # raise e
            return

        return
        '''

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
            if ctx.channel.id == property.DOWNLOAD_CHANNEL:
                await ctx.invoke(self.bot.get_command('youtube download'), url)
            elif ctx.channel.id == property.HIGHLIGHT_CHANNEL:
                await ctx.invoke(self.bot.get_command('youtube highlight'), url)

def setup(bot):
    return bot.add_cog(MainCog(bot))