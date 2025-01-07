import boto3
import urllib.request
import sys
#sudo cat /var/log/cloud-init-output.log

s3 = boto3.client('s3')
bucket_datalake = "datalake-generated-2025"

def create_bucket(bucket_name):
    try:
        print(f"Creando bucket {bucket_name}...")
        s3.create_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} creado correctamente.")
    except s3.exceptions.BucketAlreadyExists:
        print(f"El bucket {bucket_name} ya existe.")
    except Exception as e:
        print(f"Error al crear el bucket: {e}")

def fetch_file(id):
    url = f"https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt"
    try:
        print(f"Descargando archivo desde: {url}")
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                return response.read().decode("utf-8"), response.status
            else:
                print(f"Error al descargar el archivo {id}: Estado HTTP {response.status}")
                return None, response.status
    except urllib.error.URLError as e:
        print(f"Error al descargar el archivo {id}: {e.reason}")
        return None, 500

def save_file(bucket_name, id, text):
    text = text.replace("\r\n", "\n").lstrip('\ufeff')  
    try:
        print(f"Subiendo archivo {id}.txt al bucket {bucket_name}...")
        s3.put_object(Bucket=bucket_name, Key=f"{id}.txt", Body=text)
        print(f"Archivo {id}.txt subido correctamente.")
    except Exception as e:
        print(f"Error al subir archivo {id}.txt: {e}")

def upload_document(bucket_name, id):
    text, status = fetch_file(id)
    if status != 200:
        print(f"Error: El archivo {id} no pudo descargarse. Estado HTTP: {status}")
        s3.put_object(Bucket=bucket_name, Key=f"error_{id}.txt", Body=f"Error descargando archivo ID {id}, estado HTTP: {status}")
        return
    save_file(bucket_name, id, text)

if __name__ == "__main__":
    create_bucket(bucket_datalake)
    print("Ejecución iniciada...")

    for id in range(1, 10):
        upload_document(bucket_datalake, id)

        print("Archivos subidos correctamente.")
    