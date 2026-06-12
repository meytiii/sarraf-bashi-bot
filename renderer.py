import io
from pygments import highlight
from pygments.lexers import guess_lexer
from pygments.formatters import ImageFormatter
from pygments.util import ClassNotFound
import os
import urllib.request
import urllib.parse
import httpx

async def generate_code_image(code_text: str, theme: str = "monokai"):
    try:
        print(f"🎨 [LIGHTWEIGHT RENDERER] Processing snippet... (Theme: {theme})")
        
        style_map = {
            "monokai": "monokai",
            "dracula": "dracula",
            "nord": "nord-darker",
            "github": "default"
        }
        selected_style = style_map.get(theme, "monokai")
        bg_color = "#ffffff" if theme == "github" else "#1F1F24"

        try:
            lexer = guess_lexer(code_text)
        except ClassNotFound:
            from pygments.lexers.special import TextLexer
            lexer = TextLexer()

        font_filename = "JetBrainsMono-Regular.ttf"
        font_path = os.path.abspath(font_filename)
        
        if not os.path.exists(font_path):
            print("📥 [FONT] Downloading JetBrains Mono font for the cloud server...")
            try:
                font_url = "https://raw.githubusercontent.com/JetBrains/JetBrainsMono/master/fonts/ttf/JetBrainsMono-Regular.ttf"
                urllib.request.urlretrieve(font_url, font_path)
            except Exception as e:
                print(f"⚠️ [FONT WARNING]: Download failed ({e}).")

        formatter = ImageFormatter(
            style=selected_style,
            font_size=20,
            line_numbers=True,
            line_number_bg=bg_color,
            line_number_fg="#888888",
            background_color=bg_color,
            line_pad=10,
            font_name=font_path if os.path.exists(font_path) else "Courier New"
        )

        image_bytes = highlight(code_text, lexer, formatter)
        
        from PIL import Image, ImageDraw
        
        raw_img = Image.open(io.BytesIO(image_bytes))
        
        top_bar_height = 45
        padding_x = 10
        padding_y_bottom = 10
        new_width = raw_img.width + (padding_x * 2)
        new_height = raw_img.height + top_bar_height + padding_y_bottom
        
        canvas = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)
        
        draw.rounded_rectangle([(0, 0), (new_width, new_height)], radius=12, fill=bg_color)
        
        dot_radius = 6
        dot_y = 22
        dot_x = 20
        gap = 20
        
        draw.ellipse([(dot_x, dot_y - dot_radius), (dot_x + dot_radius*2, dot_y + dot_radius)], fill="#ff5f56")
        draw.ellipse([(dot_x + gap, dot_y - dot_radius), (dot_x + gap + dot_radius*2, dot_y + dot_radius)], fill="#ffbd2e")
        draw.ellipse([(dot_x + gap*2, dot_y - dot_radius), (dot_x + gap*2 + dot_radius*2, dot_y + dot_radius)], fill="#27c93f")
        
        canvas.paste(raw_img, (padding_x, top_bar_height))
        
        print("✅ [SUCCESS] Canvas painted with Mac UI in pure Python memory!")
        
        final_buffer = io.BytesIO()
        canvas.save(final_buffer, format="PNG")
        final_buffer.seek(0)
        final_buffer.name = "snippet.png"
        return final_buffer

    except Exception as e:
        print(f"⚠️ [CRITICAL PYGMENTS ERROR]: {e}")
        return None

async def generate_math_image(latex_text: str):
    """Renders formal mathematical equations using the CodeCogs API."""
    try:
        print("🧮 [MATH RENDERER] Processing formula...")
        
        # Combine the styling tags and the math formula into one string
        full_latex_query = r"\dpi{300}\bg_white\huge " + latex_text.strip()
        
        # URL encode the ENTIRE string safely, using the newer .image endpoint
        safe_query = urllib.parse.quote(full_latex_query)
        url = f"https://latex.codecogs.com/png.image?{safe_query}"
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)
        
        if response.status_code == 200:
            print("✅ [SUCCESS] Math Canvas painted!")
            img_buffer = io.BytesIO(response.content)
            img_buffer.name = "math.png"
            return img_buffer
        else:
            print(f"❌ [API ERROR] Math Renderer returned {response.status_code}")
            return None
            
    except Exception as e:
        print(f"⚠️ [CRITICAL MATH ERROR]: {e}")
        return None