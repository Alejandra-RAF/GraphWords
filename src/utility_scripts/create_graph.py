import boto3
import os

# Crear el cliente S3
s3 = boto3.client('s3')  
bucket_input = "datamart-generated-2025"  
bucket_datamart = "graph-generated-2025"

def create_bucket(bucket_name):
    try:
        print(f"Creando el bucket {bucket_name}...")
        s3.create_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} creado correctamente.")
    except s3.exceptions.BucketAlreadyExists:
        print(f"El bucket {bucket_name} ya existe.")
    except Exception as e:
        print(f"Error al crear el bucket: {e}")

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

def process_specific_files():
    specific_files = ["palabras_3.txt", "palabras_4.txt", "palabras_5.txt"]

    for file in specific_files:
        print(f"Procesando archivo específico: {file}")
        try:
            diccionario = leer_diccionario_desde_s3(bucket_input, file)
            lista_pesos = lista_palabras_pesos(diccionario)
            destination_key = f"processed_{os.path.basename(file)}"
            guardar_en_s3(bucket_datamart, destination_key, lista_pesos)
            print(f"Archivo {file} procesado y guardado como {destination_key} en {bucket_datamart}.")
        except Exception as e:
            print(f"Error al procesar {file}: {e}")

def main():
    try:
        print("Inicio del procesamiento...")
        create_bucket(bucket_datamart)  # Crear el bucket si no existe
        process_specific_files()  # Procesar los archivos específicos
        print("Procesamiento completado y resultados subidos a S3.")
    except Exception as e:
        print(f"Error en la ejecución: {e}")

if __name__ == "__main__":
    main()
