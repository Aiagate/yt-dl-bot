#! /usr/bin/env python3
import asyncio
import discord
from discord.ext import commands
import property


class SystemCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='system')
    async def botsystem(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Error: missing option')

    @botsystem.command(name='close')
    async def botsystem_close(self, ctx):
        await self.bot.get_channel(property.LOG_CHANNEL).send('Bot System Will Be Shutdown...')
        await asyncio.sleep(3)
        await self.bot.close()

    @commands.group(name='cog')
    async def cogs(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Error: missing option')

    @cogs.group(name='reload')
    async def cogs_reload(self, ctx, *args, **kwargs):
        if len(args) == 0:
            await ctx.send('Error: missing cog name opetand')
            return

        for cog in args:
            if cog == 'all':
                for cog in property.INITIAL_EXTENSIONS:
                    self.bot.reload_extension(cog)
                    await ctx.send('Success: ' + cog + ' is Reloaded.')
            else:
                self.bot.reload_extension('cogs.' + cog)
                await ctx.send('Success: cog.' + cog + ' is Reloaded.')

    @cogs_reload.error
    async def cogs_reload_error(self, ctx, error):
        await ctx.send('Error: ' + str(error))

    @cogs.group(name='load')
    async def cogs_load(self, ctx, *args, **kwargs):
        if len(args) == 0:
            await ctx.send('Error: missing cog name opetand')
            return

        for cog in args:
            if cog == 'all':
                for cog in property.INITIAL_EXTENSIONS:
                    self.bot.load_extension(cog)
                    await ctx.send('Success: ' + cog + ' is Loaded.')
            else:
                self.bot.load_extension('cogs.' + cog)
                await ctx.send('Success: cog.' + cog + ' is Loaded.')
    
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
    async def cogs_unload(self, ctx, *args, **kwargs):
        force_option = False

        if len(args) == 0:
            await ctx.send('Error: missing cog name opetand')
            return

        for cog in args:
            if cog == '-f':
                force_option = True
        
        for cog in args:
            if cog == 'all':
                if force_option == False:
                        await ctx.send("Error: can't unload. (force unload : -f)")
                        return
                for cog in property.INITIAL_EXTENSIONS:
                    self.bot.unload_extension(cog)
                    await ctx.send('Success: ' + cog + ' is Unloaded.')

            if cog == 'systemcog' and force_option == True:
                pass
            elif cog == 'systemcog' and force_option == False:
                await ctx.send("Error: systemcog can't unload. (force unload : -f)")
                return

            self.bot.unload_extension('cogs.' + cog)
            await ctx.send('Success: cog.' + cog + ' is Unloaded.')
    
    @cogs_unload.error
    async def cogs_unload_error(self, ctx, error):
        await ctx.send('Error: ' + str(error))

    @commands.command(enabled=False)
    async def send_log(self, ctx, *args, **kwargs):
        await self.bot.get_channel(property.LOG_CHANNEL).send('``' + '\n'.join(args) + '``')
    
    @commands.command(enabled=False)
    async def send_error_log(self, ctx, *args, **kwargs):
        log_channel = self.bot.get_channel(property.LOG_CHANNEL)
        await ctx.reply('Error: Check ' + log_channel.mention)
        await self.bot.get_channel(property.LOG_CHANNEL).send('**ERROR**\n' + '``' + '\n'.join(args) + '``')

    @commands.command(enabled=False)
    async def send_output_log(self, ctx, info, url):
        await self.bot.get_channel(property.OUTPUT_CHANNEL).send('**Download Success : **' + '%(title)s' % info + '\n' + url)


def setup(bot):
    return bot.add_cog(SystemCog(bot))
