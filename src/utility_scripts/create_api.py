import boto3
import json
from create_functions_api import (
    leer_diccionario_desde_s3,
    dijkstra,
    camino_mas_largo,
    detectar_nodos_aislados,
    Conectividad
)

# Configuración de S3 y variables
LOCALSTACK_URL = os.getenv('LOCALSTACK_URL', 'http://172.17.0.2:4566')
s3 = boto3.client('s3', endpoint_url=LOCALSTACK_URL)

bucket_name = 'graph'
file_name = "processed_palabras_3.txt"


def api_dijkstra(params):
    """Ruta para obtener el camino más corto usando el algoritmo de Dijkstra."""
    if not file_name:
        return {"statusCode": 404, "body": json.dumps({"message": "No se encontró el archivo en S3"})}

    _, graph = leer_diccionario_desde_s3(bucket_name, file_name)
    start_word = params.get('start')
    target_word = params.get('target')

    if not start_word or not target_word:
        return {"statusCode": 400, "body": json.dumps({"message": "Faltan parámetros 'start' y/o 'target'"})}

    path, distance = dijkstra(graph, start_word, target_word)
    if distance < float('infinity'):
        return {
            "statusCode": 200,
            "body": json.dumps({
                "start": start_word,
                "target": target_word,
                "path": path,
                "distance": distance,
                "message": "Camino más corto encontrado"
            })
        }
    else:
        return {"statusCode": 404, "body": json.dumps({"message": f"No hay un camino entre '{start_word}' y '{target_word}'"})}


def api_camino_mas_largo(params):
    """Ruta para obtener el camino más largo entre nodos."""
    if not file_name:
        return {"statusCode": 404, "body": json.dumps({"message": "No se encontró el archivo en S3"})}

    _, graph = leer_diccionario_desde_s3(bucket_name, file_name)
    start = params.get('start')
    end = params.get('end')

    if start and end:
        path, distance = camino_mas_largo(graph, start, end)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "start": start,
                "end": end,
                "path": path,
                "distance": distance,
                "message": "Camino más largo calculado"
            })
        }
    else:
        max_path, max_distance, start_word, target_word = camino_mas_largo(graph)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "start": start_word,
                "end": target_word,
                "path": max_path,
                "distance": max_distance,
                "message": "Camino más largo general calculado"
            })
        }


def api_nodos_aislados():
    """Ruta para identificar nodos aislados."""
    _, graph = leer_diccionario_desde_s3(bucket_name, file_name)
    if graph is None:
        return {"statusCode": 500, "body": json.dumps({"message": "El grafo no se pudo construir desde el archivo."})}

    nodos_aislados = detectar_nodos_aislados(graph)
    return {
        "statusCode": 200,
        "body": json.dumps({"nodos_aislados": nodos_aislados, "message": "Nodos aislados identificados"})
    }


def api_nodos_alto_grado(params):
    """Ruta para obtener nodos con alto grado de conectividad."""
    _, graph = leer_diccionario_desde_s3(bucket_name, file_name)
    conectividad = Conectividad(graph)
    umbral = params.get('umbral', 1)
    nodos_alto_grado = conectividad.nodos_alto_grado(int(umbral))

    return {
        "statusCode": 200,
        "body": json.dumps({"umbral": umbral, "nodos_alto_grado": nodos_alto_grado, "message": "Nodos con alto grado de conectividad identificados"})
    }


def api_nodos_grado_especifico(params):
    """Ruta para obtener nodos con grado específico."""
    _, graph = leer_diccionario_desde_s3(bucket_name, file_name)
    conectividad = Conectividad(graph)
    grado = params.get('grado', 1)
    nodos = conectividad.nodos_con_grado_especifico(int(grado))

    return {
        "statusCode": 200,
        "body": json.dumps({"grado": grado, "nodos": nodos, "message": "Nodos con grado específico identificados"})
    }


def main(event, context):
    """Punto de entrada de la función Lambda."""
    print(f"Prueba de importación de 'os': {os}")
    path = event.get("path", "")
    method = event.get("httpMethod", "")
    params = event.get("queryStringParameters", {})

    if path == "/camino_mas_largo" and method == "GET":
        return api_camino_mas_largo(params)
    elif path == "/Dijkstra/" and method == "GET":
        return api_dijkstra(params)
    elif path == "/nodos_aislados" and method == "GET":
        return api_nodos_aislados()
    elif path == "/nodos_alto_grado" and method == "GET":
        return api_nodos_alto_grado(params)
    elif path == "/nodos_grado_especifico" and method == "GET":
        return api_nodos_grado_especifico(params)

    return {"statusCode": 404, "body": json.dumps({"message": "Ruta no encontrada."})}

