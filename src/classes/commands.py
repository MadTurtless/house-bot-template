"""
Registers commands for the bot
"""
import logging
import os

from discord.ext import commands

from src.classes.database_manager import DatabaseManager
from src.classes.jokes_manager import Jokes
from src.classes.level_manager import LevelManager
from src.classes.quotes_manager import QuotesManager
from src.utils.helper import check_perms

logger = logging.getLogger("discord")

class Commands(commands.Cog):
    """
    The Commands class is a cog implementation that acts as a wrapper for generic commands.
    More specific functionalities can be found in their own classes.
    """
    def __init__(self, bot):
        """
        :param bot: discord.ext.commands.Bot object
        """
        self.bot = bot
        self.db = DatabaseManager()
        self.lvl_mgr = LevelManager(self.bot)
        self.joke_mgr = Jokes()
        self.quote_mgr = QuotesManager()

    @commands.hybrid_command(
        description="Get a joke. (This is from an API and randomised.)"
    )
    async def joke(self, ctx: commands.Context):
        joke = await self.bot.loop.run_in_executor(None, self.joke_mgr.get_joke)
        await ctx.send(joke)

    @commands.hybrid_command(
        description="Get a quote from GoT."
    )
    async def quote(self, ctx: commands.Context):
        quote = await self.bot.loop.run_in_executor(None, self.quote_mgr.get_quote)
        await ctx.send(quote)

    @commands.hybrid_command(
        description="Check the bot's status."
    )
    @check_perms()
    async def status(self, ctx: commands.Context):
        status = os.getenv("STATUS")
        if status == "development":
            await ctx.send("This is the development version of Baratheon Backup.\n"
                            "-# Not intended for public use.")
            return
        msg = "This is the production version of Baratheon Backup."
        if os.path.isfile("data/db.sqlite"):
            msg += "\nDatabase found."
        await ctx.send(msg)

async def setup(bot: commands.Bot):
    """
    This function adds all the commands to the bot.
    :param bot: discord.ext.commands.Bot object
    :return: void
    """
    await bot.add_cog(Commands(bot))
