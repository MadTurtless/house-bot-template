import os

from discord.ext import commands
from dotenv import load_dotenv

from src.utils.helper import get_number_suffix


class JoinManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        load_dotenv()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member:
            return

        channel_id = os.getenv("JOIN_CHANNEL_ID")
        channel = await self.bot.fetch_channel(channel_id)
        if not channel:
            return

        member_count = member.guild.member_count

        await channel.send(f"Welcome {member.mention} to **KOTR | HOUSE BARATHEON!** You are the {str(member_count) + get_number_suffix(member_count)} member!")

async def setup(bot):
    await bot.add_cog(JoinManager(bot))