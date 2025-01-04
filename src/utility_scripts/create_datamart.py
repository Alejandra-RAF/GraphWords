import boto3
import re
from collections import Counter
import os

LOCALSTACK_URL = os.getenv('LOCALSTACK_URL', 'http://172.17.0.2:4566')
print(f"Conectando a LocalStack en {LOCALSTACK_URL}")

s3 = boto3.client('s3', endpoint_url=LOCALSTACK_URL)
bucket_input = "datalake"  
bucket_output = "datamart"   


def bucket_exists(bucket_name):
    existing_buckets = s3.list_buckets()
    for bucket in existing_buckets.get('Buckets', []):
        if bucket['Name'] == bucket_name:
            return True
    return False


def create_bucket_if_not_exists(bucket_name):
    if not bucket_exists(bucket_name):
        s3.create_bucket(Bucket=bucket_name)


def get_s3_files(bucket_name):
    objects = s3.list_objects_v2(Bucket=bucket_name)
    return [obj['Key'] for obj in objects.get('Contents', [])]


def preprocesado(texto):
    palabras = texto.split()
    palabras_filtradas = []
    for palabra in palabras:
        if palabra.isalpha(): 
            if not re.search(r'[aeiou]{3,}', palabra, re.IGNORECASE) and not re.search(r'[^aeiou]{3,}', palabra, re.IGNORECASE):
                palabras_filtradas.append(palabra)
    return palabras_filtradas


def crear_diccionario_palabras_letras(texto, num_letras):
    palabras = re.findall(rf'\b\w{{{num_letras}}}\b', texto.lower())
    return Counter(palabras)


def guardar_diccionario_en_s3(diccionario, nombre_archivo, bucket_name):
    contenido = "\n".join([f"{palabra}: {frecuencia}" for palabra, frecuencia in diccionario.items()])
    s3.put_object(Bucket=bucket_name, Key=f"{nombre_archivo}.txt", Body=contenido)


def process_files():
    files = get_s3_files(bucket_input)

    diccionario_3 = Counter()
    diccionario_4 = Counter()
    diccionario_5 = Counter()

    for file_key in files:
        file_object = s3.get_object(Bucket=bucket_input, Key=file_key)
        file_content = file_object['Body'].read().decode('utf-8')

        palabras_filtradas = preprocesado(file_content)
        texto_filtrado = ' '.join(palabras_filtradas)

        diccionario_3.update(crear_diccionario_palabras_letras(texto_filtrado, 3))
        diccionario_4.update(crear_diccionario_palabras_letras(texto_filtrado, 4))
        diccionario_5.update(crear_diccionario_palabras_letras(texto_filtrado, 5))

    guardar_diccionario_en_s3(diccionario_3, "palabras_3", bucket_output)
    guardar_diccionario_en_s3(diccionario_4, "palabras_4", bucket_output)
    guardar_diccionario_en_s3(diccionario_5, "palabras_5", bucket_output)


def main(event, context):
    """Punto de entrada de la función Lambda."""
    try:
        print("Ejecución de Lambda iniciada...")
        create_bucket_if_not_exists(bucket_output)  
        process_files()  
        print("Ejecución de Lambda finalizada.")
        return {"statusCode": 200, "body": "Procesamiento completado y resultados subidos a S3"}
    except Exception as e:
        print(f"Error en la ejecución de Lambda: {e}")
        return {"statusCode": 500, "body": f"Error en la ejecución de Lambda: {e}"}
