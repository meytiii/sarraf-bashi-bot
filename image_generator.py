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
    
    reshaped_label = reshape(label_text)
    display_label = get_display(reshaped_label)
    
    reshaped_price = reshape(price_text)
    display_price = get_display(reshaped_price)
    
    label_width = draw.textlength(display_label, font=label_font)
    label_height = 36
    
    price_width = draw.textlength(display_price, font=price_font)
    price_height = 52
    
    spacing = 15
    total_height = label_height + price_height + spacing
    
    start_y = (height - total_height) / 2
    
    card_w = max(label_width, price_width) + 100
    card_h = total_height + 40
    card_x1 = (width - card_w) / 2
    card_y1 = start_y - 20
    
    draw.rounded_rectangle(
        [card_x1, card_y1, card_x1 + card_w, card_y1 + card_h],
        radius=15,
        fill=(0, 0, 0, 110)
    )

    label_x = (width - label_width) / 2
    draw.text((label_x, start_y), display_label, fill=(235, 235, 240, 180), font=label_font)
    
    price_x = (width - price_width) / 2
    price_y = start_y + label_height + spacing
    
    draw.text((price_x + 2, price_y + 2), display_price, fill=(0, 0, 0, 150), font=price_font)
    draw.text((price_x, price_y), display_price, fill=(255, 255, 255, 255), font=price_font)
    
    watermark_text = "@sarraf_bashi_bot"
    watermark_font = ImageFont.truetype(font_path, 20)
    w_width = draw.textlength(watermark_text, font=watermark_font)
    
    draw.text((width - w_width - 35, height - 45), watermark_text, fill=(255, 255, 255, 120), font=watermark_font)

    byte_io = io.BytesIO()
    img.save(byte_io, 'PNG')
    byte_io.seek(0)
    return byte_io