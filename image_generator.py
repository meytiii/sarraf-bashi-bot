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
        img = Image.new("RGBA", (1774, 887), (20, 20, 25, 255))
    else:
        img = Image.open(template_path).convert("RGBA")
        
    width, height = img.size
    draw = ImageDraw.Draw(img)
    
    font_path = os.path.join("assets", "fonts", "Vazirmatn-Bold.ttf")
    label_font = ImageFont.truetype(font_path, 64)
    price_font = ImageFont.truetype(font_path, 110)
    watermark_font = ImageFont.truetype(font_path, 32)
    
    disp_label = get_display(reshape(label_text))
    disp_price = get_display(reshape(price_text))
    
    label_width = draw.textlength(disp_label, font=label_font)
    price_width = draw.textlength(disp_price, font=price_font)
    
    label_height = 64
    price_height = 110
    spacing = 30
    total_content_height = label_height + price_height + spacing
    
    card_w = max(label_width, price_width) + 160
    card_h = total_content_height + 100
    card_x = (width - card_w) / 2
    card_y = (height - card_h) / 2
    
    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=30,
        fill=(10, 10, 12, 175)
    )
    
    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=30,
        outline=(255, 255, 255, 30),
        width=2
    )
    
    start_y = card_y + 50
    
    lx = (width - label_width) / 2
    draw.text((lx, start_y), disp_label, fill=(255, 215, 0, 230), font=label_font)
    
    px = (width - price_width) / 2
    py = start_y + label_height + spacing
    
    draw.text((px + 4, py + 4), disp_price, fill=(0, 0, 0, 180), font=price_font)
    draw.text((px, py), disp_price, fill=(255, 255, 255, 255), font=price_font)
    
    watermark_text = "SARRAF BASHI BOT  •  قیمت لحظه‌ای بازار"
    disp_wm = get_display(reshape(watermark_text))
    wm_width = draw.textlength(disp_wm, font=watermark_font)
    
    draw.text(((width - wm_width) / 2, height - 80), disp_wm, fill=(255, 255, 255, 60), font=watermark_font)

    byte_io = io.BytesIO()
    img.save(byte_io, 'PNG')
    byte_io.seek(0)
    return byte_io