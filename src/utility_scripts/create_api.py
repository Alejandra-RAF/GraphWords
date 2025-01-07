import boto3
import json
import os
from flask import Flask, request, jsonify
from create_functions_api import (
    leer_diccionario_desde_s3,
    dijkstra,
    camino_mas_largo,
    detectar_nodos_aislados,
    Conectividad,
    obtener_todos_los_caminos,
    detectar_clusters
)

# Configuración de Flask
app = Flask(__name__)

# Configuración de S3 y variables
LOCALSTACK_URL = os.getenv('LOCALSTACK_URL', 'http://172.17.0.2:4566')
s3 = boto3.client('s3', endpoint_url=LOCALSTACK_URL)

bucket_name = 'graph'
file_name = "processed_palabras_3.txt"

# --------------------------------------------
# Funciones de la API
# --------------------------------------------

def api_dijkstra(params):
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
    _, graph = leer_diccionario_desde_s3(bucket_name, file_name)
    if graph is None:
        return {"statusCode": 500, "body": json.dumps({"message": "El grafo no se pudo construir desde el archivo."})}

    nodos_aislados = detectar_nodos_aislados(graph)
    return {
        "statusCode": 200,
        "body": json.dumps({"nodos_aislados": nodos_aislados, "message": "Nodos aislados identificados"})
    }

def api_nodos_alto_grado(params):
    _, graph = leer_diccionario_desde_s3(bucket_name, file_name)
    conectividad = Conectividad(graph)
    umbral = params.get('umbral', 1)
    nodos_alto_grado = conectividad.nodos_alto_grado(int(umbral))

    return {
        "statusCode": 200,
        "body": json.dumps({"umbral": umbral, "nodos_alto_grado": nodos_alto_grado, "message": "Nodos con alto grado de conectividad identificados"})
    }

def api_nodos_grado_especifico(params):
    _, graph = leer_diccionario_desde_s3(bucket_name, file_name)
    conectividad = Conectividad(graph)
    grado = params.get('grado', 1)
    nodos = conectividad.nodos_con_grado_especifico(int(grado))

    return {
        "statusCode": 200,
        "body": json.dumps({"grado": grado, "nodos": nodos, "message": "Nodos con grado específico identificados"})
    }

def api_todos_los_caminos(params):
    _, graph = leer_diccionario_desde_s3(bucket_name, file_name)
    start_word = params.get('start')
    target_word = params.get('target')

    if not start_word or not target_word:
        return {"statusCode": 400, "body": json.dumps({"message": "Faltan parámetros 'start' y/o 'target'"})}

    all_paths = obtener_todos_los_caminos(graph, start_word, target_word)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "start": start_word,
            "target": target_word,
            "all_paths": all_paths,
            "message": "Todos los caminos calculados"
        })
    }

def api_detectar_clusters():
    _, graph = leer_diccionario_desde_s3(bucket_name, file_name)
    clusters = detectar_clusters(graph)

    return {
        "statusCode": 200,
        "body": json.dumps({"clusters": clusters, "message": "Clústeres identificados en el grafo"})
    }

# --------------------------------------------
# Función Lambda para AWS
# --------------------------------------------

def main(event, context):
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
    elif path == "/todos_los_caminos" and method == "GET":
        return api_todos_los_caminos(params)
    elif path == "/detectar_clusters" and method == "GET":
        return api_detectar_clusters()

    return {"statusCode": 404, "body": json.dumps({"message": "Ruta no encontrada."})}

# --------------------------------------------
# Rutas para el servidor Flask (modo local)
# --------------------------------------------

@app.route('/camino_mas_largo', methods=['GET'])
def flask_camino_mas_largo():
    params = request.args.to_dict()
    response = api_camino_mas_largo(params)
    return jsonify(json.loads(response["body"])), response["statusCode"]

@app.route('/Dijkstra/', methods=['GET'])
def flask_dijkstra():
    params = request.args.to_dict()
    response = api_dijkstra(params)
    return jsonify(json.loads(response["body"])), response["statusCode"]

@app.route('/nodos_aislados', methods=['GET'])
def flask_nodos_aislados():
    response = api_nodos_aislados()
    return jsonify(json.loads(response["body"])), response["statusCode"]

@app.route('/nodos_alto_grado', methods=['GET'])
def flask_nodos_alto_grado():
    params = request.args.to_dict()
    response = api_nodos_alto_grado(params)
    return jsonify(json.loads(response["body"])), response["statusCode"]

@app.route('/nodos_grado_especifico', methods=['GET'])
def flask_nodos_grado_especifico():
    params = request.args.to_dict()
    response = api_nodos_grado_especifico(params)
    return jsonify(json.loads(response["body"])), response["statusCode"]

@app.route('/todos_los_caminos', methods=['GET'])
def flask_todos_los_caminos():
    params = request.args.to_dict()
    response = api_todos_los_caminos(params)
    return jsonify(json.loads(response["body"])), response["statusCode"]

@app.route('/detectar_clusters', methods=['GET'])
def flask_detectar_clusters():
    response = api_detectar_clusters()
    return jsonify(json.loads(response["body"])), response["statusCode"]

# --------------------------------------------
# Ejecutar la aplicación Flask en modo local
# --------------------------------------------

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=4566)
