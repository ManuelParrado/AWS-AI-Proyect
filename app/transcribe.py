import boto3
import time
import requests
from dotenv import load_dotenv
import os

# Cargamos las variables de entorno
load_dotenv()

# Recuperamos las credenciales y configuraciones
access_key_id = os.environ.get('ACCESS_KEY_ID')
secret_access_key = os.environ.get('ACCESS_SECRET_KEY')
bucket_audio = os.environ.get('BUCKET_AUDIO')

# Inicializamos el cliente de Transcribe
transcribe = boto3.Session(
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
    region_name='eu-west-2'
).client('transcribe')

# Función para transcribir un archivo de audio de S3
def transcribe_audio(real_name, filename, language):
    
    try:
        # Crear un nombre único para el trabajo de transcripción
        job_name = f"transcribe-{filename.replace('.', '-')}-{int(time.time())}"

        # Iniciar el trabajo de transcripción
        response = transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': f's3://{bucket_audio}/{real_name}'},
            MediaFormat='mp3',
            LanguageCode=f'{language}'
        )
        print(f"Trabajo de transcripción '{job_name}' iniciado: {response}")

        # Monitorear el estado del trabajo
        while True:
            job_response = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            status = job_response['TranscriptionJob']['TranscriptionJobStatus']

            if status in ['COMPLETED', 'FAILED']:
                break
            time.sleep(5)

        # Procesar el resultado
        if status == 'COMPLETED':
            transcript_uri = job_response['TranscriptionJob']['Transcript']['TranscriptFileUri']
            response = requests.get(transcript_uri)
            transcription = response.json()
            transcribed_text = transcription['results']['transcripts'][0]['transcript']
            return transcribed_text

        raise Exception(f"Error en la transcripción: {job_response['TranscriptionJob']['FailureReason']}")

    except Exception as e:
        print(f"Error en la transcripción: {str(e)}")
        raise
