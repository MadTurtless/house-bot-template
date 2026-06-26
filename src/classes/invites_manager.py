import discord
from discord.ext import commands

from src.classes.database_manager import DatabaseManager
from src.utils.image_generators.invleaderboard_image import create_invleaderboard_card


class InvitesManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DatabaseManager()

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        self.db.create_invite(invite.id, invite.inviter.id)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        cached_uses_per_invite = self.db.get_uses_per_invite()

        for invite in await guild.invites():
            amount = invite.uses
            if amount > cached_uses_per_invite[invite.id]:
                used_invite_id = invite.id
                self.db.add_invite_link(used_invite_id, member.id)
                break

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        self.db.remove_invite_link(member.id)

    #Commands
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

async def setup(bot: commands.Bot):
    await bot.add_cog(InvitesManager(bot))
