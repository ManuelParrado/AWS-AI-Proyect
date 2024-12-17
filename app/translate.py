import boto3
import os
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Configuración de AWS
access_key_id = os.environ.get('ACCESS_KEY_ID')
secret_access_key = os.environ.get('ACCESS_SECRET_KEY')

# Inicializar el cliente de Translate
translate_client = boto3.Session(
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
    region_name='eu-west-2'
).client('translate')


# Traduce el texto sacado del audio al idioma que se le indique
def translate_text(text, target_language):
    try:
        
        print(text, "Archivo de tradución")
        print(target_language, "Archivo de tradución")
        
        response = translate_client.translate_text(
            Text=text,
            SourceLanguageCode='auto',  # Detecta automáticamente el idioma de origen
            TargetLanguageCode=target_language
        )
        
        print(response['TranslatedText'], "Archivo de tradución")
        
        return response['TranslatedText']
    except Exception as e:
        print(f"Error en la traducción: {str(e)}")
        raise
