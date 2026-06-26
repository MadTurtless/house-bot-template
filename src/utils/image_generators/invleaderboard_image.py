import io
from PIL import ImageDraw

from src.utils.helper import load_image_generator_background, load_image_generator_font


async def create_invleaderboard_card(ctx, users: list, bot) -> io.BytesIO:
    width, height = 1300, 600

    font_path = "src/assets/fonts/Arial-Unicode-MS.ttf"
    fallback_font_path = "src/assets/fonts/Arial-Unicode-MS.ttf"

    image = load_image_generator_background(width, height)
    draw = ImageDraw.Draw(image)

    font_title, font_sub, fallback_font = load_image_generator_font(font_path, fallback_font_path)

    for i in range(len(users)):
        u = users[i]
        y_offset = i * 110
        x_offset = 0

        if i > 4:
            x_offset = 600
            y_offset = (i - 5) * 110

        guild = ctx.guild
        user = guild.get_member(u[0])
        if not user:
            user = await bot.fetch_user(u[0])
            username = user.name
        else:
            username = user.display_name
        invites = u[1]

        draw.text((40 + x_offset, 40 + y_offset), f"{i + 1}. {username}", fill=(217, 195, 56), font=font_title)
        if i != 9:
            draw.text((76 + x_offset, 75 + y_offset), f"{invites} Invite(s)", fill=(181, 163, 51), font=font_sub)
        else:
            draw.text((93 + x_offset, 75 + y_offset), f"{invites} Invite(s)", fill=(181, 163, 51), font=font_sub)


    image_binary = io.BytesIO()
    image.save(image_binary, "PNG")
    image_binary.seek(0)

    return image_binary
