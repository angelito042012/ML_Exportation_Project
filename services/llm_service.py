from openai import OpenAI
import json
import os

class LLMExtractionService:

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

    def extract_attributes(self, text):

        prompt = f"""
Extrae los atributos del producto.

Devuelve únicamente JSON.

Campos:

- empaquetado
- ingredientes
- peso
- fecha_vencimiento
- certificaciones
- pais_origen
- etiquetado_ingles
- registro_fda

Texto:

{text}
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)
