import os
import io
import jdatetime
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from arabic_reshaper import reshape
from bidi.algorithm import get_display
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def create_trend_graph(history_data, asset_key, color):
    if not history_data or asset_key not in history_data or len(history_data[asset_key]) < 2:
        return None
        
    dates = list(history_data[asset_key].keys())
    
    values = [float(v) / 10 for v in history_data[asset_key].values()]
    
    short_dates = []
    for d in dates:
        try:
            g_date = datetime.strptime(d, "%Y-%m-%d").date()
            j_date = jdatetime.date.fromgregorian(date=g_date)
            short_dates.append(f"{j_date.month:02d}/{j_date.day:02d}")
        except:
            short_dates.append(d[5:].replace('-', '/'))
    
    fig, ax = plt.subplots(figsize=(13, 4.2), dpi=100)
    fig.patch.set_alpha(0.0)
    ax.set_facecolor((0, 0, 0, 0))
    
    min_val = min(values)
    max_val = max(values)
    padding = (max_val - min_val) * 0.15
    if padding == 0:
        padding = min_val * 0.05
    ax.set_ylim(min_val - padding, max_val + padding)
    
    ax.plot(short_dates, values, color=color, linewidth=5, marker='o', markersize=14, markerfacecolor='#1A1A1D', markeredgecolor=color, markeredgewidth=4)
    ax.fill_between(short_dates, values, min_val - padding, color=color, alpha=0.20)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('white')
    ax.spines['bottom'].set_linewidth(2)
    
    ax.tick_params(axis='x', colors='white', labelsize=16, pad=15)
    ax.tick_params(axis='y', colors='white', labelsize=16, pad=10)
    
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{int(x):,}"))
    ax.grid(axis='y', color='white', linestyle='solid', alpha=0.08)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return Image.open(buf)

def generate_price_banner(banner_type, label_text, price_text, change_val="0", change_pct="0", change_dir="", history_data=None):
    try:
        num_price = float(re.sub(r'[^\d.]', '', price_text))
        price_text = f"تومان {int(num_price / 10):,}"
    except Exception:
        pass
        
    try:
        num_change = float(re.sub(r'[^\d.]', '', str(change_val)))
        change_val = f"{int(num_change / 10):,}"
    except Exception:
        pass

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
    draw = ImageDraw.Draw(img, "RGBA")
    
    font_path = os.path.join("assets", "fonts", "Vazirmatn-Bold.ttf")
    label_font = ImageFont.truetype(font_path, 55)
    price_font = ImageFont.truetype(font_path, 110)
    change_font = ImageFont.truetype(font_path, 38)
    watermark_font = ImageFont.truetype(font_path, 32)
    
    disp_label = label_text
    disp_price = price_text
    
    if change_dir == "high":
        c_color = (0, 255, 130, 255)
        arrow = "▲"
    elif change_dir == "low":
        c_color = (255, 80, 80, 255)
        arrow = "▼"
    else:
        c_color = (200, 200, 200, 255)
        arrow = "▬"
        
    disp_change = f"{arrow} {change_val} ({change_pct}%)"
    
    label_width = draw.textlength(disp_label, font=label_font, direction="rtl")
    price_width = draw.textlength(disp_price, font=price_font, direction="rtl")
    change_width = draw.textlength(disp_change, font=change_font, direction="rtl")
    
    label_height = 55
    price_height = 110
    change_height = 38
    
    asset_map = {"usd": "usd", "coin": "coin_emami", "gold": "gold_18k"}
    color_map = {"usd": "#00E5FF", "coin": "#FFD700", "gold": "#FFD700"}
    db_key = asset_map.get(banner_type)
    accent_color = color_map.get(banner_type, "#FFFFFF")
    
    graph_img = create_trend_graph(history_data, db_key, accent_color)
    has_graph = graph_img is not None
    graph_w, graph_h = graph_img.size if has_graph else (0, 0)
    
    spacing_top_to_price = 10
    spacing_price_to_change = 15
    spacing_change_to_graph = 40
    padding_x = 240
    padding_y = 120
    
    card_w = max(label_width, price_width, change_width, graph_w) + padding_x
    card_h = label_height + spacing_top_to_price + price_height + spacing_price_to_change + change_height + (spacing_change_to_graph + graph_h if has_graph else 0) + padding_y
    
    card_x = (width - card_w) / 2
    card_y = (height - card_h) / 2 - 30
    
    draw.rounded_rectangle([card_x-8, card_y-8, card_x+card_w+8, card_y+card_h+8], radius=45, fill=(0, 0, 0, 80))
    draw.rounded_rectangle([card_x, card_y, card_x+card_w, card_y+card_h], radius=40, fill=(15, 15, 18, 220))
    draw.rounded_rectangle([card_x, card_y, card_x+card_w, card_y+card_h], radius=40, outline=(255, 255, 255, 50), width=3)
    
    start_y = card_y + int(padding_y / 2)
    lx = (width - label_width) / 2
    draw.text((lx, start_y), disp_label, fill=(255, 215, 0, 240), font=label_font, direction="rtl")
    
    px = (width - price_width) / 2
    py = start_y + label_height + spacing_top_to_price
    draw.text((px + 5, py + 5), disp_price, fill=(0, 0, 0, 200), font=price_font, direction="rtl")
    draw.text((px, py), disp_price, fill=(255, 255, 255, 255), font=price_font, direction="rtl")
    
    cx = (width - change_width) / 2
    cy = py + price_height + spacing_price_to_change
    draw.text((cx, cy), disp_change, fill=c_color, font=change_font, direction="rtl")
    
    if has_graph:
        gx = int((width - graph_w) / 2)
        gy = int(cy + change_height + spacing_change_to_graph)
        img.paste(graph_img, (gx, gy), graph_img)
    
    watermark_text = "SARRAF BASHI BOT  •  قیمت لحظه‌ای بازار"
    disp_wm = watermark_text
    wm_width = draw.textlength(disp_wm, font=watermark_font, direction="rtl")
    
    pill_pad_x = 50
    pill_pad_y = 18
    pill_w = wm_width + (pill_pad_x * 2)
    pill_h = 32 + (pill_pad_y * 2)
    pill_x = (width - pill_w) / 2
    pill_y = height - pill_h - 45 
    
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=30, fill=(0, 0, 0, 220))
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=30, outline=(255, 255, 255, 45), width=2)
    
    wm_x = pill_x + pill_pad_x
    wm_y = pill_y + pill_pad_y - 8
    draw.text((wm_x, wm_y), disp_wm, fill=(255, 255, 255, 210), font=watermark_font, direction="rtl")

    byte_io = io.BytesIO()
    img.save(byte_io, 'PNG')
    byte_io.seek(0)
    return byte_io