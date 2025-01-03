import boto3
import os

LOCALSTACK_URL = os.getenv('LOCALSTACK_URL', 'http://localhost:4566')
print(f"Conectando a LocalStack en {LOCALSTACK_URL}")

# Configuración de los buckets y el cliente S3
s3 = boto3.client('s3', endpoint_url=LOCALSTACK_URL)
bucket_input = "datamart"  
bucket_output = "graph" 


def bucket_exists(bucket_name):
    existing_buckets = s3.list_buckets()
    for bucket in existing_buckets.get('Buckets', []):
        if bucket['Name'] == bucket_name:
            return True
    return False

def create_bucket_if_not_exists(bucket_name):
    if not bucket_exists(bucket_name):
        s3.create_bucket(Bucket=bucket_name)

def get_txt_files(bucket_name):
    objects = s3.list_objects_v2(Bucket=bucket_name)
    return [obj['Key'] for obj in objects.get('Contents', []) if obj['Key'].endswith('.txt')]


def leer_diccionario_desde_s3(bucket_name, input_key):
    response = s3.get_object(Bucket=bucket_name, Key=input_key)
    content = response['Body'].read().decode('utf-8')
    diccionario = {}
    for line in content.strip().split('\n'):
        palabra, peso = line.split(": ")
        diccionario[palabra] = int(peso)
    return diccionario
    


def difieren_en_una_letra(palabra1, palabra2):
    if len(palabra1) != len(palabra2):
        return False
    diferencia = sum(1 for a, b in zip(palabra1, palabra2) if a != b)
    return diferencia == 1


def lista_palabras_pesos(diccionario):
    lista_pesos = []
    palabras = list(diccionario.keys())
    for i in range(len(palabras)):
        for j in range(i + 1, len(palabras)):
            palabra1 = palabras[i]
            palabra2 = palabras[j]
            if difieren_en_una_letra(palabra1, palabra2):
                peso1 = diccionario[palabra1]
                peso2 = diccionario[palabra2]
                peso_conexion = abs(peso1 - peso2)
                lista_pesos.append((palabra1, palabra2, peso_conexion))
    return lista_pesos


def guardar_en_s3(bucket_name, key, lista_pesos):
    contenido = "\n".join([f"{palabra1} {palabra2} {peso}" for palabra1, palabra2, peso in lista_pesos])
    s3.put_object(Bucket=bucket_name, Key=key, Body=contenido)
       
def process_files():
    txt_files = get_txt_files(bucket_input)
    files_with_3 = [file for file in txt_files if '3' in file]


    for file in files_with_3:
        print(f"Procesando archivo específico: {file}")
        diccionario = leer_diccionario_desde_s3(bucket_input, file)
        lista_pesos = lista_palabras_pesos(diccionario)
        destination_key = f"processed_{os.path.basename(file)}"
        guardar_en_s3(bucket_output, destination_key, lista_pesos)



def main(event, context):
    try:
        print("Ejecución de Lambda iniciada...")
        create_bucket_if_not_exists(bucket_output)
        process_files()
        print("Ejecución de Lambda finalizada.")
        return {"statusCode": 200, "body": "Procesamiento completado y resultados subidos a S3"}
    except Exception as e:
        print(f"Error en la ejecución de Lambda: {e}")
        return {"statusCode": 500, "body": f"Error: {e}"}
