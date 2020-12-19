#! /usr/bin/env python3
import asyncio
import discord
from discord.ext import commands
import property


class SystemCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='bot')
    async def botsystem(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Error: Need Option!')

    @botsystem.command(name='close')
    async def botsystem_close(self, ctx):
        await self.bot.get_channel(property.LOG_CHANNEL).send('Bot System Will Be Shutdown...')
        await asyncio.sleep(3)
        await self.bot.close()

    @commands.group(name='cog')
    async def cogs(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Error: Need Option!')

    @cogs.group(name='reload')
    async def cogs_reload(self, ctx):
        args = ctx.message.content.split()

        if len(args) <= 2:
            await ctx.send('Error: Need Cog Name!')

        for index, cog in enumerate(args):
            if 2 <= index:
                self.bot.reload_extension('cogs.' + cog)
                await ctx.send('Success: cog.' + cog + ' is Reloaded.')
            else:
                pass

    @cogs_reload.error
    async def cogs_reload_error(self, ctx, error):
        await ctx.send('Error: ' + str(error))

    @cogs_reload.command(name='all')
    async def cogs_reload_all(self, ctx):
        print('')

    @cogs_reload_all.error
    async def cogs_reloadall_error(self, ctx, error):
        await ctx.send('Error: ' + str(error))

    @cogs.group(name='load')
    async def cogs_load(self, ctx):
        args = ctx.message.content.split()

        if len(args) <= 2:
            await ctx.send('Error: Need Cog Name!')

        for index, cog in enumerate(args):
            if 2 <= index:
                self.bot.load_extension('cogs.' + cog)
                await ctx.send('Success: cog.' + cog + ' is Loaded.')
            else:
                pass
    
    @cogs_load.error
    async def cogs_load_error(self, ctx, error):
        await ctx.send('Error: ' + str(error))

    @cogs_load.command(name='all')
    async def cogs_load_all(self, ctx):
        pass
    
    @cogs_load_all.error
    async def cogs_load_all_error(self, ctx, error):
        await ctx.send('Error: ' + str(error))

    @cogs.group(name='unload')
    async def cogs_unload(self, ctx):
        args = ctx.message.content.split()
        force_option = False

        if len(args) <= 2:
            await ctx.send('Error: Need Cog Name!')

        for index, cog in enumerate(args):
            if cog.startswith('-'):
                if cog in 'f':
                    force_option = True
                else:
                    pass
            else:
                pass
                
            if 2 <= index:
                if cog == 'systemcog' and force_option == True:
                    pass
                elif cog == 'systemcog' and force_option == False:
                    await ctx.send("Error: systemcog can't unload. (force unload : -f)")
                    return

                self.bot.unload_extension('cogs.' + cog)
                await ctx.send('Success: cog.' + cog + ' is Unloaded.')
            else:
                pass
    
    @cogs_unload.error
    async def cogs_unload_error(self, ctx, error):
        await ctx.send('Error: ' + str(error))


def setup(bot):
    return bot.add_cog(SystemCog(bot))
