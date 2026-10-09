import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print('ERROR: No se encontro GEMINI_API_KEY en el archivo .env')
    exit(1)

# Endpoint oficial de Gemini
url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}'
headers = {'Content-Type': 'application/json'}
payload = {
    'contents': [{
        'parts': [{'text': 'Hola, responde en una sola oracion corta: Que es un commit en Git?'}]
    }]
}

print('Enviando peticion autenticada a la API de Gemini...')
response = requests.post(url, json=payload, headers=headers)

print(f'Codigo de estado: {response.status_code}')

if response.status_code == 200:
    data = response.json()
    texto = data['candidates'][0]['content']['parts'][0]['text']
    print('\n[EXITO - RESPUESTA DEL MODELO]:')
    print(texto.strip())
else:
    print('\n[ERROR EN LA PETICION]:')
    print(response.text)
