import os
import io
from PIL import Image, ImageDraw, ImageFont
from arabic_reshaper import reshape
from bidi.algorithm import get_display
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def create_trend_graph(history_data, asset_key, color):
    if not history_data or asset_key not in history_data or len(history_data[asset_key]) < 2:
        return None
        
    dates = list(history_data[asset_key].keys())
    short_dates = [d[5:].replace('-', '/') for d in dates]
    values = list(history_data[asset_key].values())
    
    fig, ax = plt.subplots(figsize=(10, 3), dpi=100)
    fig.patch.set_alpha(0.0)
    ax.set_facecolor((0, 0, 0, 0))
    
    ax.plot(short_dates, values, color=color, linewidth=4, marker='o', markersize=10, markerfacecolor='white', markeredgecolor=color, markeredgewidth=3)
    ax.fill_between(short_dates, values, color=color, alpha=0.15)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('white')
    
    ax.tick_params(axis='x', colors='white', labelsize=14, pad=10)
    ax.tick_params(axis='y', colors='white', labelsize=12)
    ax.grid(axis='y', color='white', linestyle='--', alpha=0.1)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return Image.open(buf)

def generate_price_banner(banner_type, label_text, price_text, history_data=None):
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
    label_font = ImageFont.truetype(font_path, 48)
    price_font = ImageFont.truetype(font_path, 86)
    watermark_font = ImageFont.truetype(font_path, 28)
    
    disp_label = get_display(reshape(label_text))
    disp_price = get_display(reshape(price_text))
    
    label_width = draw.textlength(disp_label, font=label_font)
    price_width = draw.textlength(disp_price, font=price_font)
    
    label_height = 48
    price_height = 86
    spacing = 20
    total_content_height = label_height + price_height + spacing
    
    asset_map = {"usd": "usd", "coin": "coin_emami", "gold": "gold_18k"}
    color_map = {"usd": "#00E5FF", "coin": "#FFD700", "gold": "#FFD700"}
    db_key = asset_map.get(banner_type)
    accent_color = color_map.get(banner_type, "#FFFFFF")
    
    graph_img = create_trend_graph(history_data, db_key, accent_color)
    has_graph = graph_img is not None
    graph_w, graph_h = graph_img.size if has_graph else (0, 0)
    
    card_w = max(label_width, price_width, graph_w) + 160
    card_h = total_content_height + (graph_h + 40 if has_graph else 100)
    
    card_x = (width - card_w) / 2
    card_y = (height - card_h) / 2 - 30
    
    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=30, fill=(10, 10, 12, 180))
    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=30, outline=(255, 255, 255, 40), width=2)
    
    start_y = card_y + 40
    lx = (width - label_width) / 2
    draw.text((lx, start_y), disp_label, fill=(255, 215, 0, 240), font=label_font)
    
    px = (width - price_width) / 2
    py = start_y + label_height + spacing
    draw.text((px + 4, py + 4), disp_price, fill=(0, 0, 0, 180), font=price_font)
    draw.text((px, py), disp_price, fill=(255, 255, 255, 255), font=price_font)
    
    if has_graph:
        gx = int((width - graph_w) / 2)
        gy = int(py + price_height + 30)
        img.paste(graph_img, (gx, gy), graph_img)
    
    watermark_text = "SARRAF BASHI BOT  •  قیمت لحظه‌ای بازار"
    disp_wm = get_display(reshape(watermark_text))
    wm_width = draw.textlength(disp_wm, font=watermark_font)
    
    pad_x = 40
    pad_y = 15
    pill_w = wm_width + (pad_x * 2)
    pill_h = 28 + (pad_y * 2)
    pill_x = (width - pill_w) / 2
    pill_y = height - pill_h - 40
    
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=25, fill=(0, 0, 0, 200))
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=25, outline=(255, 255, 255, 50), width=1)
    
    wm_x = pill_x + pad_x
    wm_y = pill_y + pad_y - 5
    draw.text((wm_x, wm_y), disp_wm, fill=(255, 255, 255, 200), font=watermark_font)

    byte_io = io.BytesIO()
    img.save(byte_io, 'PNG')
    byte_io.seek(0)
    return byte_io