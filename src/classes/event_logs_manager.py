"""
Handles listening for event logs and parsing the data to hand off to the database manager.

Expected format:
    Event Type: [Type Name]
    Host: [@Mention]
    Participants: [@Mention1, @Mention2, ...]
    Proof: [Attached Image or Link]
Note: the proof line is ignored by the parser.
"""
import asyncio
import logging
import os
import sys

from discord.ext import commands
from dotenv import load_dotenv

from src.classes.database_manager import DatabaseManager
from src.utils.helper import parse_event_log, get_original_log

logger = logging.getLogger("discord")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - [%(levelname)s] - %(message)s",
                    handlers=[
                        logging.FileHandler(filename="discord.log", encoding="utf-8", mode="a+"),
                              logging.StreamHandler(stream=sys.stdout)
                    ])

load_dotenv()

def validate_event_log(log):
    """
    Validates the log dict has the required keys.
    """
    required = ["type", "host_id", "participants"]
    return all(item in log for item in required)

class EventLogsManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DatabaseManager()

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Listens for any message sent in the server.
        This is then filtered to only messages that are both not from the bot and in one of the specified channels.
        When a message meets these criteria, it is handed off to the helper to parse the data into a dictionary.

        If the dictionary returns as invalid, an error message will be sent and it, along with the message, will self-destruct.
        """
        if message.author.bot:
            return

        if not message.channel.id == int(os.getenv("LOGS_CHANNEL_ID")):
            return

        log = parse_event_log(message)

        if not validate_event_log(log):
            logger.warning(f"Invalid log from user {message.author}: '{message.content}'")
            await message.reply("Invalid log. Please check the log and try again.", delete_after=5)
            await asyncio.sleep(10)
            await message.delete()
            return

        self.db.add_event(log)
        await message.add_reaction("\u2705")

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        """
        Listens for any message edited in the server.
        This is then filtered to only messages that are not from the bot and in one of the specified channels.
        When a message meets these criteria, it is compared to the previous interation (rebuilt from the data stored in the database).

        If the event type or number of attendees are changed, the db entry is updated.
        """

        if payload.message.author.bot:
            return

        if not payload.message.channel.id == int(os.getenv("LOGS_CHANNEL_ID")):
            return

        old_log = get_original_log(payload.message.id)
        new_log = parse_event_log(payload.message)

        new_users = []

        for u_id in new_log["participants"]:
            if not int(u_id) in old_log["participants"]:
                new_users.append(u_id)

        if new_users:
            self.db.add_event_participants(old_log["event_id"], new_users)
            logger.info(
                f"Event log {old_log['msg_id']} updated. Changed attendees from {old_log['participants']} -> {new_log['participants']}")
            await payload.message.reply("Event log updated successfully, new attendees added!", delete_after=5)


        if new_log["type"] != old_log["type"]:
            self.db.update_event_type(old_log["event_id"], new_log["type"])
            logger.info(f"Event log {old_log['msg_id']} updated. Changed type to {new_log['type']}")
            await payload.message.reply("Event log updated successfully, type changed!", delete_after=5)



async def setup(bot):
    await bot.add_cog(EventLogsManager(bot))

