import json
import logging
import math
import os
import time
from pathlib import Path

import discord
from discord.ext import commands, tasks

from src.classes.database_manager import DatabaseManager
from src.utils.helper import qualifies_for_xp, is_server_booster

logger = logging.getLogger("discord")

def _lvl_reqs() -> dict[int, int]:
    """
    Generates a dictionary containing the xp requirements for each level.
    The requirements increase exponentially by a factor of 1.5.
    """
    lvl_rqs = {}
    base_xp = 100
    for i in range(0, 200):
        req = math.ceil((base_xp * (i ** 1.5)) / 100) * 100
        lvl_rqs[i] = req
    return lvl_rqs


class LevelManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = DatabaseManager()
        self._cooldowns = {}
        self.lvl_reqs = _lvl_reqs()

        # Performance Cache
        self.channel_id = int(os.getenv("XP_EARNABLE_CHANNEL_ID", 0))
        self.lvl_up_channel_id = int(os.getenv("LEVEL_UP_MSG_CHANNEL_ID", 0))

        with open(Path("data/level_roles.json"), "r") as f:
            self.lvl_roles = json.load(f)

        self.clean_cooldown_dict.start()

    def cog_unload(self):
        """Cleanly stop background loops when the cog is reloaded/unloaded."""
        self.clean_cooldown_dict.cancel()

    def get_lvl_reqs(self) -> dict[int, int]:
        return self.lvl_reqs

    @tasks.loop(hours=1)
    async def clean_cooldown_dict(self):
        """Cleans expired entries from the cooldown dictionary to prevent memory bloat."""
        current_time = time.time()
        self._cooldowns = {uid: exp for uid, exp in list(self._cooldowns.items()) if exp > current_time}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        if message.channel.id != self.channel_id:
            return

        if not qualifies_for_xp(message.content):
            return

        author_id = message.author.id
        current_time = time.time()
        cooldown_expiry = self._cooldowns.get(author_id, 0)

        if current_time < cooldown_expiry:
            return

        self._cooldowns[author_id] = current_time + 1

        try:
            if not self.db.get_user(author_id):
                self.db.add_user(author_id)

            base_xp = 5
            if is_server_booster(message):
                base_xp *= 2

            self.db.add_user_xp(author_id, base_xp)
            user_xp = self.db.get_user_xp(author_id)
            current_lvl = self.db.get_user_level(author_id)
            next_lvl = current_lvl + 1

            if next_lvl in self.lvl_reqs and user_xp >= self.lvl_reqs[next_lvl]:
                self.db.add_user_level(author_id, 1)
                guild = message.guild

                if str(next_lvl) in self.lvl_roles:
                    role = guild.get_role(int(self.lvl_roles[str(next_lvl)]))
                    if role:
                        await message.author.add_roles(role)

                notification_channel = guild.get_channel(self.lvl_up_channel_id)
                if notification_channel:
                    await notification_channel.send(
                        f"{message.author.mention} congratulations on achieving level {next_lvl}!"
                    )
                logger.info(f"User {message.author} has achieved level {next_lvl}")

        except Exception:
            logger.exception(f"An error occurred handling XP updates for User {author_id}")


async def setup(bot: commands.Bot):
    await bot.add_cog(LevelManager(bot))