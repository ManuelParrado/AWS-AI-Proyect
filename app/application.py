# Importamos las librerías necesarias
import boto3
import os
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Importar la función de transcribir
from transcribe import transcribe_audio 

# Importar la función de traducción
from translate import translate_text

# Importar la función para la creación del audios
from speech_synthesis import generate_audio

# Cargamos las variables de entorno
load_dotenv()

# Recuperamos las credenciales y configuraciones
access_key_id = os.environ.get('ACCESS_KEY_ID')
secret_access_key = os.environ.get('ACCESS_SECRET_KEY')
bucket_audio = os.environ.get('BUCKET_AUDIO')

# Creamos la aplicación Flask
application = Flask(__name__)
# Le aplicamos CORS, para que las peticiones http funcionen correctamente
CORS(application)

# Creamos una instancia del servicio S3
s3 = boto3.Session(
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key).resource('s3')

# Endpoint de prueba
@application.route('/api/try', methods=['GET'])
def try_server():
    return Response("Servidor en funcionamiento", status=200, content_type="text/plain")

# Endpoint para subir archivos a S3
@application.route('/api/upload_record_to_s3', methods=['POST'])
def upload_record_to_s3():
    try:
        # Obtén el archivo del request
        file = request.files.get('file')
        
        # Valida que se haya recibido un archivo
        if not file:
            print("No se encontró un archivo en la solicitud.")
            return Response("No se encontró un archivo en la solicitud", status=400)

        # Sube el archivo a S3
        print(f"Subiendo el archivo '{file.filename}' a S3...")
        s3.Bucket(bucket_audio).put_object(Key=file.filename, Body=file)
        print(f"Archivo '{file.filename}' subido exitosamente a S3.")

        # Responde con éxito
        return Response(f"Archivo '{file.filename}' subido correctamente a S3.", status=200)
    
    except Exception as e:
        print(f"Error al subir el archivo: {str(e)}")
        return Response(f"Error al subir el archivo: {str(e)}", status=500)


# Endpoint para obtener los nombres de las grabaciones, para mostrarlas en el desplegable
@application.route('/api/get_all_record_from_s3', methods=['GET'])
def get_all_record_from_s3():
    try:
        # Listar todos los objetos (archivos) del bucket
        print(f"Listando todos los archivos en el bucket '{bucket_audio}'...")
        bucket = s3.Bucket(bucket_audio)
        files = [{"name": obj.key} for obj in bucket.objects.all()]

        # Verificar si se encontraron archivos
        if not files:
            print("No se encontraron archivos en el bucket.")
            return Response("No se encontraron archivos en el bucket.", status=404)

        print(f"Archivos encontrados: {files}")
        return jsonify(files)  # Devuelve una lista en formato JSON
    except Exception as e:
        print(f"Error al obtener los archivos del bucket: {str(e)}")
        return Response(f"Error al obtener los archivos del bucket: {str(e)}", status=500)


# Endpoint para llamar a la función de transcripción
@application.route('/api/transcribe_selected_record', methods=['GET'])
def transcribe_selected_record_endpoit():
    try:
        real_name = request.args.get('realName')
        filename = request.args.get('filename')
        language = request.args.get('language')
        
        # Validación
        if not filename:
            return Response("No se proporcionó un nombre de archivo.", status=400)

        # Llamar a la función de transcripción
        transcribed_text = transcribe_audio(real_name, filename, language)

        # Devolver el texto transcrito
        return jsonify({'transcription': transcribed_text})

    except Exception as e:
        print(f"Error en la transcripción: {str(e)}")
        return Response(f"Error en la transcripción: {str(e)}", status=500)
    

# Endpoint para hacer la traducción del texto sacado del audio
@application.route('/api/translate_text_from_transcribe', methods=['POST'])
def translate_text_endpoint():
    
    try:
        data = request.json
        text = data.get('text')
        target_language = data.get('language')

        # Validación
        if not text or not target_language:
            return Response("Faltan datos: 'text' y/o 'language'.", status=400)

        # Llamar a la función de traducción
        translated_text = translate_text(text, target_language)

        # Responder con el texto traducido
        return jsonify({'translated_text': translated_text})

    except Exception as e:
        print(f"Error en la traducción: {str(e)}")
        return Response(f"Error en la traducción: {str(e)}", status=500)
    

# Endpoint para llamar a la función de generación de audios
@application.route('/api/synthesize_speech', methods=['POST'])
def synthesize_speech_function():
    try:
        data = request.json
        text = data.get('text')
        language_code = data.get('language')

        # Validación
        if not text or not language_code:
            return Response("Faltan datos: 'text' y/o 'language'.", status=400)

        # Llamar a la función para generar el audio
        audio_stream = generate_audio(text, language_code)

        # Devolver el audio como respuesta binaria
        return Response(
            audio_stream,
            content_type='audio/mpeg',
            headers={"Content-Disposition": "attachment; filename=audio.mp3"}
        )
    except Exception as e:
        print(f"Error en el endpoint de síntesis de voz: {e}")
        return Response(f"Error en el endpoint de síntesis de voz: {e}", status=500)


# Inicia el servidor
if __name__ == "__main__":
    application.debug = True
    application.run(port=5000)  # Disponible en http://127.0.0.1:5000/
