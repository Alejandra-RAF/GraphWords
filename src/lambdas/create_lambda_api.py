import boto3
import zipfile
import os
import subprocess
import shutil
import sys

LOCALSTACK_URL = os.getenv('LOCALSTACK_URL', 'http://172.17.0.2:4566')
print(f"Conectando a LocalStack en {LOCALSTACK_URL}")

# Configuración para LocalStack
lambda_client = boto3.client('lambda', endpoint_url=LOCALSTACK_URL)
s3_client = boto3.client('s3', endpoint_url=LOCALSTACK_URL)

def create_bucket(bucket_name):
    """Crear un bucket S3 en LocalStack."""
    try:
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' creado exitosamente.")
    except Exception as e:
        print(f"Error al crear el bucket: {e}")

def install_dependencies(output_dir):
    try:
        print("Instalando dependencias en el directorio de empaquetado...")
        subprocess.check_call([os.sys.executable, "-m", "pip", "install", "flask", "werkzeug", "aiohttp", "-t", output_dir])
        print("Dependencias instaladas exitosamente.")
    except Exception as e:
        print(f"Error al instalar dependencias: {e}")

def create_zip_file(source_dir, zip_name):
    """Crear un archivo ZIP con el código Lambda y dependencias."""
    try:
        with zipfile.ZipFile(zip_name, 'w') as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    print(f"Incluyendo en ZIP: {file_path}") 
                    zipf.write(file_path, arcname=os.path.relpath(file_path, source_dir))
        print(f"Archivo ZIP creado correctamente: {zip_name}")
    except Exception as e:
        print(f"Error al crear el archivo ZIP: {e}")

def upload_to_s3(bucket_name, file_name, key):
    """Subir un archivo al bucket S3."""
    try:
        s3_client.upload_file(file_name, bucket_name, key)
        print(f"Archivo '{file_name}' subido exitosamente a '{bucket_name}/{key}'.")
    except Exception as e:
        print(f"Error al subir el archivo a S3: {e}")

def create_lambda_function(function_name, handler, bucket_name, script_key):
    """Crear una función Lambda en LocalStack."""
    try:
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.9',
            Role='arn:aws:iam::123456789012:role/dummy-role',  # Rol ficticio
            Handler=handler,
            Code={'S3Bucket': bucket_name, 'S3Key': script_key},
            Timeout=120,
            MemorySize=128
        )
        function_arn = response['FunctionArn']
        print(f"Función Lambda '{function_name}' creada con ARN: {function_arn}")
        return function_arn
    except Exception as e:
        print(f"Error al crear la función Lambda: {e}")

def main():
    bucket_name = 'lambda-deployments-bucket'
    package_dir = 'lambda_package'         # Directorio para empaquetar el código
    zip_file = 'script_Api.zip'               # Nombre del archivo ZIP
    script_key = 'script_api.zip'             # Clave del archivo en S3
    function_name = "LambdaScriptApi"
    handler = "create_api.main" 

    # Archivos necesarios
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Directorio del script actual
    script_files = [
        os.path.join(current_dir, '../utility_scripts/create_api.py'),  # Script principal
        os.path.join(current_dir, '../utility_scripts/create_functions_api.py')  # Dependencia necesaria
    ]

    # Crear el bucket S3
    create_bucket(bucket_name)

    # Crear directorio temporal para empaquetar dependencias y script
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)  # Eliminar si existe
    os.makedirs(package_dir)

    # Copiar script al directorio
    for file in script_files:
        shutil.copy(file, package_dir)

    # Instalar dependencias en el directorio
    install_dependencies(package_dir)

    # Crear archivo ZIP
    create_zip_file(package_dir, zip_file)

    # Subir el archivo ZIP a S3
    upload_to_s3(bucket_name, zip_file, script_key)

    # Crear la función Lambda
    create_lambda_function(
        function_name=function_name,
        handler=handler,
        bucket_name=bucket_name,
        script_key=script_key
    )

    # Limpiar archivos temporales
    if os.path.exists(zip_file):
        os.remove(zip_file)
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    print("Limpieza completada.")


if __name__ == '__main__':
    main()
