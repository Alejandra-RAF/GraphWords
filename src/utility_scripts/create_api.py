import boto3
import json
from flask import Flask, request, jsonify
import os
from werkzeug.datastructures import ImmutableMultiDict
from create_functions_api import (
    leer_diccionario_desde_s3,
    dijkstra,
    camino_mas_largo,
    detectar_nodos_aislados,
    Conectividad
)

# Inicializar aplicación Flask
app = Flask(__name__)

LOCALSTACK_URL = os.getenv('LOCALSTACK_URL', 'http://172.17.0.2:4566')
print(f"Conectando a LocalStack en {LOCALSTACK_URL}")

# Configuración S3
s3 = boto3.client('s3', endpoint_url=LOCALSTACK_URL)  # Cambiar si no usas LocalStack

bucket_name = 'graph'
file_name = "processed_palabras_3.txt"



@app.route('/Dijkstra/', methods=['GET'])
def api_dijkstra():
    """Ruta para obtener el camino más corto usando el algoritmo de Dijkstra."""
    try:
        if not file_name:
            return jsonify({"message": "No se encontró el archivo en S3"}), 404

        _, graph = leer_diccionario_desde_s3(bucket_name, file_name)

        start_word = request.args.get('start')
        target_word = request.args.get('target')

        if not start_word or not target_word:
            return jsonify({"message": "Faltan parámetros 'start' y/o 'target'"}), 400

        path, distance = dijkstra(graph, start_word, target_word)

        if distance < float('infinity'):
            return jsonify({
                "start": start_word,
                "target": target_word,
                "path": path,
                "distance": distance,
                "message": "Camino más corto encontrado"
            }), 200
        else:
            return jsonify({"message": f"No hay un camino entre '{start_word}' y '{target_word}'"}), 404
    except Exception as e:
        return jsonify({"message": f"Error en Dijkstra: {str(e)}"}), 500


@app.route('/camino_mas_largo', methods=['GET'])
def api_camino_mas_largo():
    """Ruta para obtener el camino más largo entre nodos."""
    try:
        if not file_name:
            return jsonify({"message": "No se encontró el archivo en S3"}), 404

        _, graph = leer_diccionario_desde_s3(bucket_name, file_name)

        start = request.args.get('start')
        end = request.args.get('end')

        if start and end:
            path, distance = camino_mas_largo(graph, start, end)
            return jsonify({
                "start": start,
                "end": end,
                "path": path,
                "distance": distance,
                "message": "Camino más largo calculado"
            }), 200
        else:
            max_path, max_distance, start_word, target_word = camino_mas_largo(graph)
            return jsonify({
                "start": start_word,
                "end": target_word,
                "path": max_path,
                "distance": max_distance,
                "message": "Camino más largo general calculado"
            }), 200
    except Exception as e:
        return jsonify({"message": f"Error en camino más largo: {str(e)}"}), 500


@app.route('/nodos_aislados', methods=['GET'])
def api_nodos_aislados():
    """Ruta para identificar nodos aislados."""
    try:
        _, graph = leer_diccionario_desde_s3(bucket_name, file_name)
        if graph is None:
            print("El grafo es None. Asegúrate de que leer_diccionario_desde_s3 está funcionando correctamente.")
            return jsonify({"message": "El grafo no se pudo construir desde el archivo."}), 500

        print("Grafo recibido para nodos aislados:", graph)  # Depuración
        nodos_aislados = detectar_nodos_aislados(graph)

        return jsonify({
            "nodos_aislados": nodos_aislados,
            "message": "Nodos aislados identificados"
        }), 200
    except Exception as e:
        return jsonify({"message": f"Error en nodos aislados: {str(e)}"}), 500


@app.route('/nodos_alto_grado', methods=['GET'])
def api_nodos_alto_grado():
    """Ruta para obtener nodos con alto grado de conectividad."""
    try:
        if not file_name:
            return jsonify({"message": "No se encontró el archivo en S3"}), 404

        _, graph = leer_diccionario_desde_s3(bucket_name, file_name)
        conectividad = Conectividad(graph)

        umbral = request.args.get('umbral', default=1, type=int)
        nodos_alto_grado = conectividad.nodos_alto_grado(umbral)

        return jsonify({
            "umbral": umbral,
            "nodos_alto_grado": nodos_alto_grado,
            "message": "Nodos con alto grado de conectividad identificados"
        }), 200
    except Exception as e:
        return jsonify({"message": f"Error en nodos alto grado: {str(e)}"}), 500


@app.route('/nodos_grado_especifico', methods=['GET'])
def api_nodos_grado_especifico():
    """Ruta para obtener nodos con grado específico."""
    try:
        if not file_name:
            return jsonify({"message": "No se encontró el archivo en S3"}), 404

        _, graph = leer_diccionario_desde_s3(bucket_name, file_name)
        conectividad = Conectividad(graph)

        grado = request.args.get('grado', default=1, type=int)
        nodos = conectividad.nodos_con_grado_especifico(grado)

        return jsonify({
            "grado": grado,
            "nodos": nodos,
            "message": "Nodos con grado específico identificados"
        }), 200
    except Exception as e:
        return jsonify({"message": f"Error en nodos grado específico: {str(e)}"}), 500




def main(event, context):
    # Verifica que el evento contenga queryStringParameters
    if not event or not event.get("queryStringParameters"):
        return {
            "statusCode": 400,
            "body": json.dumps({"mensaje": "Evento vacío o parámetros faltantes. Por favor, envía parámetros válidos."})
        }
    
    # Obtén los parámetros 'start' y 'end' de la consulta
    start = event["queryStringParameters"].get("start")
    end = event["queryStringParameters"].get("end")

    # Valida que ambos parámetros existan
    if not start or not end:
        return {
            "statusCode": 400,
            "body": json.dumps({"mensaje": "Parámetros 'start' y 'end' son obligatorios."})
        }
    
    # Log para ver los valores en CloudWatch
    print(f"Parámetro start: {start}, Parámetro end: {end}")
    print("Evento completo recibido:", json.dumps(event, indent=2))

    # Devuelve una respuesta simulando un procesamiento exitoso
    return {
        "statusCode": 200,
        "body": json.dumps({
            "mensaje": "Evento recibido correctamente",
            "start": start,
            "end": end,
            "evento": event  # Esto incluye todo el evento recibido para depuración
        })
    }


    # Crear contexto de Flask
    with app.test_request_context(
        path=path,
        method=event.get('httpMethod', 'GET'),
        query_string=ImmutableMultiDict(event.get('queryStringParameters') or {})
    ):
        response = app.full_dispatch_request()
        print("Respuesta generada por Flask:", {
            "statusCode": response.status_code,
            "headers": dict(response.headers),
            "body": response.get_data(as_text=True)
        })
        return {
            "statusCode": response.status_code,
            "headers": dict(response.headers),
            "body": response.get_data(as_text=True)
        }

#if __name__ == '__main__':
#    app.run(debug=True)
