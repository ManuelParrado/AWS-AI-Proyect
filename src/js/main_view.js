document.addEventListener('DOMContentLoaded', () => {  
    
    const server_route = 'http://127.0.0.1:5000/';

    // --- Declaración de elementos del DOM

    // Notificaciones
    const successAlert = document.getElementById('successAlert');
    const errorAlert = document.getElementById('errorAlert');
    const successAlertText = document.getElementById('successAlertText');
    const errorAlertText = document.getElementById('errorAlertText');

    // Formulario de subida de grabaciones
    const uploadRecordButton = document.getElementById('uploadRecordButton');
    const fileInput = document.getElementById('file');

    // Desplegable de grabaciones
    const recordingsDropdown = document.getElementById('recordingsDropdown');

    // Formulario de transcripción 
    const transcribeButton = document.getElementById('transcribeButton');
    const languagesDropdown = document.getElementById('languagesDropdown');
    const transcriptionResult = document.getElementById('transcriptionResult');

    // Formulario de traducción
    const translateSection = document.getElementById('translateSection');
    const translateButton = document.getElementById('translateButton');
    const translateResult = document.getElementById('translateResult');
    const translateLanguagesDropdown = document.getElementById('translateLanguagesDropdown');

    // Generación de audio
    const audioPlayer = document.getElementById('audioPlayer');
    const downloadLink = document.getElementById('downloadLink');
    const playAudioButton = document.getElementById('playAudioButton');

    // --- Declaración de elementos del DOM


    // Función para mostrar mensajes de estado
    function showAlert(type, message) {
        if (type === 'success') {
            successAlert.classList.remove('hidden');
            successAlertText.textContent = message;
        } else if (type === 'error') {
            errorAlert.classList.remove('hidden');
            errorAlertText.textContent = message;
        }

        // Ocultar cualquier alerta previa después de 5 segundos
        setTimeout(() => {
            successAlert.classList.add('hidden');
            errorAlert.classList.add('hidden');
        }, 5000);
    }


    // Función para traducir el texto transcrito
    async function translateText() {

        const transcription = transcriptionResult.textContent.trim();
        const targetLanguage = translateLanguagesDropdown.value;

        if (!targetLanguage) {
            showAlert('error', "Por favor, selecciona un idioma para traducir.");
            return;
        }

        if (!transcription) {
            showAlert('error', "Ha ocurrido un problema con la transcripción.");
            return;
        }

        translateResult.textContent = "Traduciendo...";
        try {
            const translate_response = await fetch(`${server_route}api/translate_text_from_transcribe`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: transcription,
                    language: targetLanguage,
                })
            });
    
            if (!translate_response.ok) {
                throw new Error(`Error en la traducción: ${await translate_response.text()}`);
            }
    
            const result = await translate_response.json();
            translateResult.innerHTML = `${result.translated_text}`;

            showAlert('success', "Texto traducido correctamente.");
            generateAndPlayAudio(result.translated_text);           
            
        } catch (error) {
            console.error("Error al procesar:", error);
            showAlert('error', `Error al traducir: ${error.message}`);
        }
    }    


    // Función para generar y reproducir el audio de texto traducido
    async function generateAndPlayAudio(translated_text_for_audio) {
        const targetLanguage = translateLanguagesDropdown.value;
    
        try {
            const response = await fetch(`${server_route}api/synthesize_speech`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: translated_text_for_audio,
                    language: targetLanguage,
                }),
            });
    
            if (!response.ok) {
                throw new Error(`Error al generar el audio: ${await response.text()}`);
            }
    
            // Convertir la respuesta binaria en un objeto URL
            const audioBlob = await response.blob();
            const audioUrl = URL.createObjectURL(audioBlob);
    
            console.log("Audio generado correctamente:", audioUrl);

            // Mostrar botón de reproducción
            playAudioButton.classList.remove('hidden');

            // Reproducir el audio
            audioPlayer.src = audioUrl;
            audioPlayer.play();
            
            // Mostrar el enlace de descarga del audio
            downloadLink.href = audioUrl;
            downloadLink.textContent = "Descargar Audio";
            downloadLink.download = "audio.mp3";
            downloadLink.classList.remove('hidden');

            showAlert('success', "Audio generado correctamente.");
        } catch (error) {
            console.error("Error al generar y reproducir el audio:", error);
            showAlert('error', `Error al generar el audio: ${error.message}`);
        }
    }


    // Función para formatear el nombre del archivo
    function sanitizeFilename(filename) {
        return filename.replace(/[^a-zA-Z0-9._-]/g, '-');
    }
    

    // Función para manejar la transcripción
    async function transcribeRecording() {
        let selectedRecording = recordingsDropdown.value;
        const selectedLanguage = languagesDropdown.value;

        console.log(selectedRecording)
    
        if (!selectedRecording) {
            showAlert('error', "Por favor, selecciona una grabación.");
            return;
        }
    
        if (!selectedLanguage) {
            showAlert('error', "Por favor, selecciona un idioma.");
            return;
        }
    
        const sanitizedRecording = sanitizeFilename(selectedRecording);
    
        transcriptionResult.textContent = "Procesando la transcripción...";
    
        try {
            const response = await fetch(`${server_route}/api/transcribe_selected_record?realName=${selectedRecording}&filename=${sanitizedRecording}&language=${selectedLanguage}`, {
                method: 'GET',
            });
    
            if (!response.ok) {
                throw new Error(`Error en la transcripción: ${await response.text()}`);
            }
    
            const result = await response.json();
            transcriptionResult.textContent = `${result.transcription}`;

            translateSection.classList.remove('hidden');

            showAlert('success', "Transcripción completada.");
        } catch (error) {
            transcriptionResult.textContent = `Error: ${error.message}`;
            showAlert('error', `Error al transcribir: ${error.message}`);
        }
    }


    // Función para cargar grabaciones en el dropdown
    async function loadRecordings() {
        try {
            const response = await fetch(`${server_route}/api/get_all_record_from_s3`, {
                method: 'GET',
            });

            if (!response.ok) {
                throw new Error("Error al obtener las grabaciones");
            }

            const recordings = await response.json();

            // Limpiar el desplegable antes de agregar nuevas opciones
            recordingsDropdown.innerHTML = ''; // Borra todas las opciones existentes

            recordings.forEach(recording => {
                const option = document.createElement('option');
                option.value = recording.name;
                option.textContent = recording.name;
                recordingsDropdown.appendChild(option);
            });

            console.log("Grabaciones cargadas correctamente:", recordings);
        } catch (error) {
            console.error("Error al cargar las grabaciones:", error);
            showAlert('error', "No hay grabaciones disponibles.");
        }
    }


    // Función para manejar la subida del archivo
    async function handleFileUpload(event) {
        event.preventDefault();
    
        const file = fileInput.files[0];
    
        if (!file) {
            showAlert('error', "Por favor, selecciona un archivo antes de subir.");
            return;
        }
    
        const formData = new FormData();
        formData.append('file', file);
    
        try {
            const response = await fetch(`${server_route}api/upload_record_to_s3`, {
                method: 'POST',
                body: formData,
            });
    
            if (!response.ok) {
                throw new Error(`Error al subir el archivo: ${await response.text()}`);
            }

            const result = await response.text();
            showAlert('success', "Archivo subido correctamente.");
            await loadRecordings();
        } catch (error) {
            showAlert('error', `Error al subir el archivo: ${error.message}`);
        }
    }

    // Inicializar eventos
    loadRecordings();

    uploadRecordButton.addEventListener('click', handleFileUpload);

    transcribeButton.addEventListener('click', async () => {
        transcribeButton.disabled = true; 
    
        await transcribeRecording();
    
        transcribeButton.disabled = false;
    });

    translateButton.addEventListener('click', async (event) => {
        event.preventDefault();
        translateButton.disabled = true;
    
        await translateText();
    
        translateButton.disabled = false;
    });

    playAudioButton.addEventListener('click', () => {
        audioPlayer.play();
    });
});
