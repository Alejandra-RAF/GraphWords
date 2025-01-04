import boto3
import os
import sys
import urllib.request

LOCALSTACK_URL = os.getenv('LOCALSTACK_URL', 'http://172.17.0.2:4566')
print(f"Conectando a LocalStack en {LOCALSTACK_URL}")

s3 = boto3.client('s3', endpoint_url=LOCALSTACK_URL)
bucket_datalake = "datalake"
def bucket_exists(bucket_name):
    existing_buckets = s3.list_buckets()
    for bucket in existing_buckets.get('Buckets', []):
        if bucket['Name'] == bucket_name: return True
    return False

def create_bucket_if_not_exists(bucket_name, region=None):
    if bucket_exists(bucket_name): return

    bucket_params = {'Bucket': bucket_name}
    s3.create_bucket(**bucket_params)

def fetch_file(id):
    url = f"https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt"
    with urllib.request.urlopen(url) as response:
        if response.status == 200:
            return response.read().decode("utf-8"), response.status
        else:
            print(f"Error al descargar el archivo {id}: Estado HTTP {response.status}")
            return None, response.status

def save_file(id, text):
    text = text.replace("\r\n", "\n")
    text = text.lstrip('\ufeff') 

    s3.put_object(Bucket=bucket_datalake, Key=f"{id}.txt", Body=text)

def upload_document(id):
    text, status = fetch_file(id)
    if status != 200:
        print(f"Error: El archivo {id} no pudo descargarse. Estado HTTP: {status}")
        return
    save_file(id, text)


def main(event, context):
    try:
        print("Ejecución de Lambda iniciada...")
        create_bucket_if_not_exists(bucket_datalake)
        for id in range(1, 3): 
            upload_document(id)
        print("Ejecución de Lambda finalizada.")
        return {"statusCode": 200, "body": "Archivos subidos exitosamente a S3 y guardados en el Datalake local"}
    except Exception as e:
        print(f"Error en la ejecución de la Lambda: {e}")
