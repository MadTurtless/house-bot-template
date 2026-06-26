"""
Registers commands for the bot
"""
import logging
import os

import discord
from discord.ext import commands

from src.classes.database_manager import DatabaseManager
from src.classes.jokes_manager import Jokes
from src.classes.level_manager import LevelManager
from src.classes.quotes_manager import QuotesManager
from src.utils.helper import check_perms, build_events_embed, permitted_roles
from src.utils.image_generators.invleaderboard_image import create_invleaderboard_card
from src.utils.image_generators.leaderboard_image import create_leaderboard_card
from src.utils.image_generators.profile_image import create_profile_card

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
        description="Check how many and which events you have attended."
    )
    async def events(self, ctx: commands.Context, user: discord.User):
        is_high_rank = any(role.id in permitted_roles for role in ctx.author.roles)
        is_self = user.id == ctx.author.id

        if not (is_high_rank or is_self):
            await ctx.send("You don't have enough permissions to run this command for another user!", delete_after=5)
            return

        res = self.db.get_events_by_user(user.id)
        if res == -1:
            await ctx.send("An error occurred while getting events by user.")
        else:
            await ctx.send(embed=await build_events_embed(res, user, ctx))

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
        description="Check another user's profile"
    )
    @check_perms()
    async def uprofile(self, ctx: commands.Context, user: discord.User):
        """
        This function generates an image using Pillow that contains information about the user's level,
        xp and xp needed to reach the next level.
        :param ctx:
        :param user:
        :return:
        """
        await ctx.defer()

        if not self.db.get_user(user.id):
            self.db.add_user(user.id)

        current_lvl = self.db.get_user_level(user.id)

        current_xp = self.db.get_user_xp(user.id)
        xp_needed = self.lvl_mgr.get_lvl_reqs()[current_lvl + 1]
        previous_xp_needed = self.lvl_mgr.get_lvl_reqs()[current_lvl]

        img_buffer = await self.bot.loop.run_in_executor(
            None,
            create_profile_card,
            user.display_name, current_lvl, current_xp, xp_needed, previous_xp_needed
        )

        file = discord.File(img_buffer, filename="profile.png")

        await ctx.send(file=file)

    @commands.hybrid_command(
        description="Check your current level and progress towards the next one."
    )
    async def profile(self, ctx: commands.Context):
        user = ctx.author
        await self.uprofile(ctx, user)

    @commands.hybrid_command(
        description="Check the top ten users with most xp."
    )
    async def leaderboard(self, ctx: commands.Context):
        """
        This function generates an image using Pillow that contains information about the top ten users' level and xp.
        :param ctx:
        :return:
        """
        await ctx.defer()

        users = self.db.get_top_ten_users()

        img_buffer = await create_leaderboard_card(ctx, users, self.bot)
        file = discord.File(img_buffer, filename="leaderboard.png")

        await ctx.send(file=file)

    @commands.hybrid_command(
        description="Check how many people you've invited."
    )
    async def invites(self, ctx: commands.Context):
        await self.uinvites(ctx, ctx.author)

    @commands.hybrid_command(
        description="Check how many people another user has invited."
    )
    async def uinvites(self, ctx: commands.Context, user: discord.User):
        invites = self.db.get_invites_by_user(user.id)
        amount = len(invites)

        if amount == 1:
            await ctx.send(f"{user.display_name} has {amount} invite!")
        else:
            await ctx.send(f"{user.display_name} has {amount} invites!")

    @commands.hybrid_command(
        description="Check the top ten users who have invited the most people"
    )
    async def invleaderboard(self, ctx: commands.Context):
        inviters = self.db.get_top_inviters()



        img_buffer = await create_invleaderboard_card(ctx, inviters, self.bot)
        file = discord.File(img_buffer, filename="leaderboard.png")

        await ctx.send(file=file)

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
