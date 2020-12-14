#! /usr/bin/env python3
import discord
from discord.ext import commands
import asyncio
import time
import os
import shutil

class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('pong!')

    @commands.command()
    async def test(self, ctx):
        time.sleep(60)
        await ctx.send(ctx.message.content)

    @commands.command()
    async def stoploop(self, ctx):
        # print(asyncio.get_running_loop())
        loop = asyncio.get_event_loop()
        await ctx.send(loop)
        loop.stop()

    @commands.command()
    async def move(self, ctx):
        shutil.move('/home/dorothy/work/python/discord_Youtube-dlBot/tmp/20201211_[Official] Rain ／ Nardis [Call].mkv', '/home/dorothy/')
        # print(file)

    @commands.command()
    async def loop(self, ctx):
        loop = asyncio.get_running_loop()
        loop.stop()
        loop.close()
        await ctx.send(loop.is_running())
    
    @commands.command(name='close')
    async def close_client(self, ctx):
        await self.bot.close()

def setup(bot):
    return bot.add_cog(TestCog(bot))
