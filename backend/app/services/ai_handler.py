from google import genai

from app.config import settings
from pathlib import Path

import time
import random

def configure_ai():
    if not settings.GEMINI_API_KEYS:
        print("ERROR: FLATA LA GEMINI_API_KEY en el .env")
        return False
    return True

def rewrite_news(text_content: str, category: str):
    if not configure_ai():
        return "Error: LA IA NO SE HA CONFIGURADO"
    
    max_retries = len(settings.GEMINI_API_KEYS) * 2
    
    for attempt in range(max_retries):
        
        current_key = random.choice(settings.GEMINI_API_KEYS)
        
        try:
            client = genai.Client(api_key=current_key)
            
            prompt = f"""
            Rol: Eres un redactor senior de un blog de {category} muy popular.
            
            Información Base (Fuente cruda):
            "{text_content[:4000]}"
            
            TU MISIÓN:
            Crea una nota ORIGINAL y ATRACTIVA basada en la fuente. 
            NO hagas un resumen aburrido. Reescribe la historia con un tono fresco, profesional pero enganchante.
            
            REGLAS DE FORMATO (OBLIGATORIAS PARA PARSEO):
            1. La PRIMERA línea debe ser el TITULAR (Impactante, estilo clickbait ético, max 12 palabras).
            2. Deja EXACTAMENTE UNA línea vacía después del titular.
            3. El cuerpo de la nota debe ser fluido. Usa párrafos cortos.
            4. NO uses Markdown (negritas, cursivas, #). Solo texto plano limpio.
            
            Ejemplo de estructura de salida:
            La Inteligencia Artificial acaba de cambiar las reglas del juego

            Apple sorprendió a todos esta mañana con su nuevo anuncio. Lejos de ser una actualización menor, la compañía presentó...

            Lo más interesante es cómo esto afecta a los desarrolladores, quienes ahora tendrán acceso a herramientas que antes costaban millones...
            """
            
            response = client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=prompt
            )
            return response.text.strip()
        
        except Exception as e:
            error_msg = str(e)
            
            if "429" in error_msg:
                print(f"Llave agotada. Cambiando a otra... ")
                continue
            print(f"Error IA Irrecuperable: {error_msg}")
            return f"ERROR GENERANDO CONTENIDO: {str(e)}"
    
    print("Se agotaron TODAS las llaves. Esperando 10s antes de rendirnos...")
    time.sleep(10)
    return "Error: Se excedió el número de intentos con la IA."