import discord
from discord.ext import commands

from src.classes.database_manager import DatabaseManager


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

async def setup(bot: commands.Bot):
    await bot.add_cog(InvitesManager(bot))
