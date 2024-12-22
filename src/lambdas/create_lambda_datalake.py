import boto3
import zipfile
import os
import subprocess  # Para ejecutar comandos en la terminal
import shutil      # Para manejar directorios

# Configuración para LocalStack
lambda_client = boto3.client('lambda', endpoint_url="http://localhost:4566")
s3_client = boto3.client('s3', endpoint_url="http://localhost:4566")

def create_bucket(bucket_name):
    """Crear un bucket S3 en LocalStack."""
    try:
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' creado exitosamente.")
    except Exception as e:
        print(f"Error al crear el bucket: {e}")

def install_dependencies(output_dir):
    """Instalar dependencias en un directorio."""
    try:
        print("Instalando dependencias en el directorio de empaquetado...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp", "-t", output_dir])
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
    current_dir = os.path.dirname(os.path.abspath(__file__))
    script_file = os.path.join(current_dir, '../utility_scripts/create_datalake.py')
    package_dir = 'lambda_package'         # Directorio para empaquetar el código
    zip_file = 'script_Datalake.zip'               # Nombre del archivo ZIP
    script_key = 'script_Datalake.zip'             # Clave del archivo en S3
    function_name = "LambdaScriptDatalake"
    handler = "create_datalake.main" # Handler de tu Lambda

    # Crear el bucket S3
    create_bucket(bucket_name)

    # Crear directorio temporal para empaquetar dependencias y script
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)  # Eliminar si existe
    os.makedirs(package_dir)

    # Copiar script al directorio
    shutil.copy(script_file, package_dir)

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

#Listar Funciones Lambda -> aws --endpoint-url=http://localhost:4566 lambda list-functions
#Invocar Lambda -> aws --endpoint-url=http://localhost:4566 lambda invoke --function-name LambdaScriptDatalake output.json
#Mirar si el bucket existe -> aws --endpoint-url=http://localhost:4566 s3 ls
#Verificar los archivosde s3 -> aws --endpoint-url=http://localhost:4566 s3 ls s3://datalake/

