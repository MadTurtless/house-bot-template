import io
from PIL import Image, ImageDraw, ImageFont

from src.utils.helper import is_ascii, load_image_generator_font, load_image_generator_background


def create_profile_card(username: str, level: int, current_xp: int, next_lvl_xp: int, previous_xp_needed: int) -> io.BytesIO:
    width, height = 600, 200

    font_path = "src/assets/fonts/Ancient Medium.ttf"
    fallback_font_path = "src/assets/fonts/Arial-Unicode-MS.ttf"

    image = load_image_generator_background(width, height)
    draw = ImageDraw.Draw(image)

    font_title, font_sub, fallback_font = load_image_generator_font(font_path, fallback_font_path)

    left, top, right, bottom = font_title.getbbox(username)

    draw.text((40, 40), username, fill=(217, 195, 56), font=font_title)
    if not is_ascii(username):
        draw.text((right + 20, 38), username[-1], fill=(217, 195, 56), font=fallback_font)
    draw.text((40, 80), f"Level {level}", fill=(181, 163, 51), font=font_sub)
    draw.text((430, 80), f"{current_xp} / {next_lvl_xp} XP", fill=(255, 255, 255), font=font_sub)

    draw.text((40, 150), f"{previous_xp_needed}", fill=(255, 255, 255), font=font_sub)
    draw.text((560, 150), f"{next_lvl_xp}", fill=(255, 255, 255), font=font_sub, anchor="ra")
    bar_x1, bar_y1 = 40, 120
    bar_x2, bar_y2 = 560, 145
    bar_width = bar_x2 - bar_x1

    xp_ratio = min((current_xp - previous_xp_needed) / (next_lvl_xp - previous_xp_needed), 1.0) if next_lvl_xp > 0 else 0
    fill_width = int(bar_width * xp_ratio)

    draw.rounded_rectangle([bar_x1, bar_y1, bar_x2, bar_y2], radius=12, fill=(20, 20, 20, 180))

    if fill_width > 0:
        draw.rounded_rectangle([bar_x1, bar_y1, bar_x1 + fill_width, bar_y2], radius=12, fill=(217, 195, 56))

    image_binary = io.BytesIO()
    image.save(image_binary, "PNG")
    image_binary.seek(0)

    return image_binary
