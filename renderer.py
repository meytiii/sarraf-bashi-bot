import io
from pygments import highlight
from pygments.lexers import guess_lexer
from pygments.formatters import ImageFormatter
from pygments.util import ClassNotFound
import os
import urllib.request

async def generate_code_image(code_text: str, theme: str = "monokai"):
    """Renders the code canvas using pure Python. Zero external browsers required."""
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

        font_filename = "UbuntuMono-Regular.ttf"
        font_path = os.path.abspath(font_filename)
        
        if not os.path.exists(font_path):
            print("📥 [FONT] Downloading UbuntuMono font for the cloud server...")
            font_url = "https://github.com/google/fonts/raw/main/ofl/ubuntumono/UbuntuMono-Regular.ttf"
            urllib.request.urlretrieve(font_url, font_path)

        formatter = ImageFormatter(
            style=selected_style,
            font_size=20,
            line_numbers=True,
            line_number_bg=bg_color,
            line_number_fg="#888888",
            background_color=bg_color,
            line_pad=10,
            font_name=font_path 
        )

        image_bytes = highlight(code_text, lexer, formatter)
        
        print("✅ [SUCCESS] Canvas painted in pure Python memory!")
        
        img_buffer = io.BytesIO(image_bytes)
        img_buffer.name = "snippet.png"
        return img_buffer

    except Exception as e:
        print(f"⚠️ [CRITICAL PYGMENTS ERROR]: {e}")
        return None