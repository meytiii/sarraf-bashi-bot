import os
import io
from PIL import Image, ImageDraw, ImageFont
from arabic_reshaper import reshape
from bidi.algorithm import get_display

def generate_price_banner(banner_type, label_text, price_text):
    banner_mapping = {
        "usd": "banner_usd.png",
        "coin": "banner_coin.png",
        "gold": "banner_gold.png"
    }
    
    template_name = banner_mapping.get(banner_type, "banner_usd.png")
    template_path = os.path.join("assets", template_name)
    
    if not os.path.exists(template_path):
        img = Image.new("RGBA", (800, 400), (30, 30, 35, 255))
    else:
        img = Image.open(template_path).convert("RGBA")
        
    width, height = img.size
    draw = ImageDraw.Draw(img)
    
    font_path = os.path.join("assets", "fonts", "Vazirmatn-Bold.ttf")
    label_font = ImageFont.truetype(font_path, 36)
    price_font = ImageFont.truetype(font_path, 52)
    
    raw_full_text = f"{label_text}: {price_text}"
    reshaped_text = reshape(raw_full_text)
    final_text_rtl = get_display(reshaped_text)
    
    text_width = draw.textlength(final_text_rtl, font=price_font)
    text_height = 52
    
    x_pos = (width - text_width) / 2
    y_pos = (height - text_height) / 2
    
    x_pos = (width - text_width) / 2
    y_pos = (height - text_height) / 2 - 10
    
    shadow_offset = 3
    draw.text((x_pos + shadow_offset, y_pos + shadow_offset), final_text_rtl, fill=(0, 0, 0, 180), font=price_font)
    draw.text((x_pos, y_pos), final_text_rtl, fill=(255, 255, 255, 255), font=price_font)
    
    watermark_text = "@sarraf_bashi_bot"
    watermark_font = ImageFont.truetype(font_path, 20)
    w_bbox = draw.textbbox((0, 0), watermark_text, font=watermark_font)
    w_width = w_bbox[2] - w_bbox[0]
    w_height = w_bbox[3] - w_bbox[1]
    
    w_x = width - w_width - 25
    w_y = height - w_height - 35
    
    draw.text((w_x + 1, w_y + 1), watermark_text, fill=(0, 0, 0, 100), font=watermark_font)
    draw.text((w_x, w_y), watermark_text, fill=(255, 255, 255, 120), font=watermark_font)
    
    
    byte_io = io.BytesIO()
    img.save(byte_io, 'PNG')
    byte_io.seek(0)
    return byte_io