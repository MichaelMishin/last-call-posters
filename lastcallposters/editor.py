from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os
from datetime import datetime, timedelta

# Scaled environment variables
TEXT_SCALE = float(os.getenv("TEXT_SCALE", 0.04))
PADDING_SCALE = float(os.getenv("PADDING_SCALE", 0.02))
CORNER_RADIUS_SCALE = float(os.getenv("CORNER_RADIUS_SCALE", 0.02))
HORIZONTAL_ALIGN = os.getenv("HORIZONTAL_ALIGN", "left").lower()
VERTICAL_ALIGN = os.getenv("VERTICAL_ALIGN", "bottom").lower()
HORIZONTAL_OFFSET_SCALE = float(os.getenv("HORIZONTAL_OFFSET_SCALE", 0.015))
VERTICAL_OFFSET_SCALE = float(os.getenv("VERTICAL_OFFSET_SCALE", 0.015))

def add_leaving_soon_badge(image_path: Path, output_path: Path, add_date: str, delete_after_days: int) -> Path:
    print(f"Editing image: {image_path}")
    with Image.open(image_path).convert("RGBA") as img:
        width, height = img.size

        # Create a transparent overlay
        overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        # Parse the new date format
        add_date_obj = datetime.strptime(add_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        end_date = add_date_obj + timedelta(days=delete_after_days)
        
        # Format the date as "Aug 20 / Jan 3 / Feb 18" (remove leading zero manually)
        end_date_str = end_date.strftime("%b %d").replace(" 0", " ")
        print(f"End date for badge: {end_date_str}")

        # Scaled values
        font_size = int(height * TEXT_SCALE)
        padding = int(height * PADDING_SCALE)
        corner_radius = int(height * CORNER_RADIUS_SCALE)
        horizontal_offset = int(height * HORIZONTAL_OFFSET_SCALE)
        vertical_offset = int(height * VERTICAL_OFFSET_SCALE)

        # Set the font size and load the AvenirNextLTPro-Bold font
        font_path = "fonts/AvenirNextLTPro-Bold.ttf" 
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            print(f"Font not found at {font_path}. Falling back to default font.")
            font = ImageFont.load_default()

        text = f"Leaving {end_date_str}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        badge_width = text_width + 2 * padding
        badge_height = text_height + 2 * padding

        # Horizontal alignment
        if HORIZONTAL_ALIGN == "center":
            x_position = (width - badge_width) // 2 + horizontal_offset
        elif HORIZONTAL_ALIGN == "right":
            x_position = width - badge_width - horizontal_offset
        else:  # left
            x_position = horizontal_offset

        # Vertical alignment
        if VERTICAL_ALIGN == "middle":
            y_position = (height - badge_height) // 2 + vertical_offset
        elif VERTICAL_ALIGN == "top":
            y_position = vertical_offset
        else:  # bottom
            y_position = height - badge_height - vertical_offset

        badge_box = [(x_position, y_position), (x_position + badge_width, y_position + badge_height)]
        draw.rounded_rectangle(badge_box, radius=corner_radius, fill=(255, 0, 0, 110))  # Semi-transparent red

        text_x = x_position + (badge_width - text_width) // 2
        text_y = y_position + (badge_height - text_height) // 2
        draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255, 255))

        # Composite the overlay with the original image
        combined = Image.alpha_composite(img, overlay)
        combined.save(output_path)
        print(f"Edited image saved to: {output_path}")
        return output_path
