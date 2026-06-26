import logging
import math
import os
from collections import Counter
from datetime import datetime

import discord
from PIL import Image, ImageFont
from discord.ext import commands

from src.classes.database_manager import DatabaseManager

logger = logging.getLogger("discord")

permitted_roles = [1509936313565184232, 1509939355618119760, 1509940198778081471,
                   1509941110821097544, 1509940476256456845, 1509957141262241965]

mgr = DatabaseManager()

def check_perms():
    async def predicate(ctx):
        for role in ctx.author.roles:
            if role.id in permitted_roles:
                return True

        await ctx.send("You don't have enough permissions to run this command.", delete_after=5)
        return False
    return commands.check(predicate)

async def build_setup_embed():
    embed = discord.Embed(
        title="Reaction Roles",
        colour=discord.Colour.blue(),
        description="""
            **Continents**
            \U0001F1FF\U0001F1E6: Africa
            \U0001F1E8\U0001F1F3: Asia
            \U0001F1E6\U0001F1FA: Australia
            \U0001F1EA\U0001F1FA: Europe
            \U0001F1FA\U0001F1F8: North America
            \U0001F1E7\U0001F1F7: South America
            """
    )
    return embed

async def build_events_embed(data, user, ctx):
    guild = ctx.guild

    desc = ""
    for entry in data:
        event = mgr.get_event(entry[1])
        channel = guild.get_channel(event[4])
        msg = await channel.fetch_message(event[5])
        timestamp = datetime.fromisoformat(event[3]).strftime("%d/%m/%Y %H:%M")
        desc += (f"**{event[2]}:**\n"
                 f"`{timestamp}`\n"
                 f"{msg.jump_url}\n\n")

    embed = discord.Embed(
        title=f"Events for {user.name}",
        colour=discord.Colour.yellow(),
        description=desc
    )
    return embed

def parse_event_log(message):
    lines = message.content.split("\n")

    log = {}
    for line in lines:
        match line.split(": ", 1):
            case [key, value] if value.strip():
                match key:
                    case "Event Type":
                        log["type"] = value
                    case "Host":
                        log["host_id"] = int(value.strip("<@!> "))
                    case "Attendees":
                        raw_ids = value.replace(",", " ").split(" ")
                        log["participants"] = [p.strip("<@!> ") for p in raw_ids if p.strip()]
    log["timestamp"] = datetime.now()
    log["channel_id"] = message.channel.id
    log["msg_id"] = message.id

    try:
        log["participants"].append(log["host_id"])
    except KeyError:
        pass
    return log

def get_original_log(msg_id):
    event = mgr.get_event_by_msg_id(msg_id)
    log = {
        "type": event[2],
        "host_id": event[3],
        "participants": [],
        "timestamp": datetime.now(),
        "channel_id": event[5],
        "msg_id": event[6]
    }

    event_id = event[0]
    log["event_id"] = event_id

    attendees = mgr.get_event_participants(event_id)
    for i in attendees:
        log["participants"].append(i[0])

    return log


def get_number_suffix(number):
    last_two_digits = number % 100

    if last_two_digits in [11, 12, 13]:
        return "th"

    match last_two_digits % 10:
        case 1:
            return "st"
        case 2:
            return "nd"
        case 3:
            return "rd"
        case _:
            return "th"

def calc_shannon_entropy(text: str):
    """Implementation of Shannon Entropy to determine the complexity of the message"""
    if not text:
        return 0.0

    if len(text) < 3:
        return 0.0

    counts = Counter(text)
    total_chars = len(text)

    entropy = 0.0
    for count in counts.values():
        p = count / total_chars
        entropy -= p * math.log2(p)

    return entropy

def qualifies_for_xp(text: str) -> bool:
    text = text.strip()
    length = len(text)

    if length < 5:
        return False

    entropy = calc_shannon_entropy(text)

    if length < 15:
        return entropy >= 2.2
    elif length < 50:
        return entropy >= 2.8
    else:
        return entropy >= 3.5

def is_server_booster(msg):
    guild = msg.guild
    booster_role_id = int(os.getenv("BOOSTER_ROLE_ID"))
    booster_role = guild.get_role(booster_role_id)

    for role in msg.author.roles:
        if role.id == booster_role.id:
            return True

    return False

def is_ascii(s):
    """Returns True if the string contains only standard ASCII characters."""
    try:
        s.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False

def load_image_generator_background(width, height):
    bg_path = "src/assets/images/profile-bg.png"

    try:
        background = Image.open(str(bg_path)).convert("RGB")
        image = background.resize((width, height), Image.Resampling.LANCZOS)
    except IOError:
        logger.info(f"Could not find background image at {bg_path}, using fallback.")
        image = Image.new("RGB", (width, height), (24, 25, 28))

    return image

def load_image_generator_font(font_path, fallback_font_path):
    try:
        font_title = ImageFont.truetype(str(font_path), 32)
        font_sub = ImageFont.truetype(str(font_path), 24)
        fallback_font = ImageFont.truetype(str(fallback_font_path), 32)
    except IOError:
        font_title = font_sub = ImageFont.load_default()
        fallback_font = ImageFont.load_default()

    return font_title, font_sub, fallback_font
