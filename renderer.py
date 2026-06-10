import io
import httpx

async def generate_code_image(code_text: str, theme: str = "monokai"):
    try:
        api_url = "https://carbonara.solopov.dev/api/cook"
        
        payload = {
            "code": code_text,
            "backgroundColor": "#1F1F24",
            "theme": theme,
            "exportSize": "2x",
            "paddingVertical": "30px",
            "paddingHorizontal": "30px"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, json=payload)
        
        if response.status_code == 200:
            return io.BytesIO(response.content)
        else:
            print(f"Renderer API returned status code: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error rendering code image: {e}")
        return None