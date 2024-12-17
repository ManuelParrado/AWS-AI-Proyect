import boto3
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de AWS
access_key_id = os.environ.get('ACCESS_KEY_ID')
secret_access_key = os.environ.get('ACCESS_SECRET_KEY')

# Crear cliente de Amazon Polly
polly_client = boto3.Session(
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
    region_name='eu-west-2'  # Cambia según tu región
).client('polly')

# Función para generar un audio con Polly
def generate_audio(text, language_code):
    try:
        # Configurar voz según el idioma
        voice_id = "Joanna"  # Voz predeterminada
        voices = {
            "es": "Lucia",       # Español (España)
            "es-MX": "Mia",      # Español (Latinoamérica)
            "en": "Joanna",      # Inglés (General)
            "en-GB": "Amy",      # Inglés (Británico)
            "fr": "Celine",      # Francés
            "de": "Vicki",       # Alemán
            "it": "Carla",       # Italiano
            "pt": "Camila",      # Portugués (Brasil)
            "zh": "Zhiyu",       # Chino Simplificado
            "ja": "Mizuki"       # Japonés
        }
        
        # Configurar voz basada en el codigo del idioma
        voice_id = voices.get(language_code, voice_id)

        # Generar el audio con Polly
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            VoiceId=voice_id
        )

        # Retornar el flujo de audio
        return response['AudioStream'].read()
    except Exception as e:
        print(f"Error al generar audio con Polly: {e}")
        raise
