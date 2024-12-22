import boto3
import json
from flask import Flask, request, jsonify
from werkzeug.datastructures import ImmutableMultiDict
from create_functions_api import (
    obtener_nombre_archivo_en_s3,
    leer_diccionario_desde_s3,
    dijkstra,
    camino_mas_largo,
    detectar_nodos_aislados,
    Conectividad
)

# Inicializar aplicación Flask
app = Flask(__name__)

# Configuración S3
s3 = boto3.client('s3', endpoint_url="http://localhost:4566")  # Cambiar si no usas LocalStack
bucket_name = 'datamart'


def s3_file_exists(bucket_name, prefix=""):
    """Verifica si hay archivos disponibles en el bucket con un prefijo."""
    file_key = obtener_nombre_archivo_en_s3(bucket_name, prefix)
    if not file_key:
        return None
    return file_key


@app.route('/Dijkstra/', methods=['GET'])
def api_dijkstra():
    """Ruta para obtener el camino más corto usando el algoritmo de Dijkstra."""
    try:
        file_key = s3_file_exists(bucket_name)
        if not file_key:
            return jsonify({"message": "No se encontró el archivo en S3"}), 404

        _, graph = leer_diccionario_desde_s3(bucket_name, file_key)

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
        file_key = s3_file_exists(bucket_name)
        if not file_key:
            return jsonify({"message": "No se encontró el archivo en S3"}), 404

        _, graph = leer_diccionario_desde_s3(bucket_name, file_key)

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
        file_key = s3_file_exists(bucket_name)
        if not file_key:
            return jsonify({"message": "No se encontró el archivo en S3"}), 404

        _, graph = leer_diccionario_desde_s3(bucket_name, file_key)
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
        file_key = s3_file_exists(bucket_name)
        if not file_key:
            return jsonify({"message": "No se encontró el archivo en S3"}), 404

        _, graph = leer_diccionario_desde_s3(bucket_name, file_key)
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
        file_key = s3_file_exists(bucket_name)
        if not file_key:
            return jsonify({"message": "No se encontró el archivo en S3"}), 404

        _, graph = leer_diccionario_desde_s3(bucket_name, file_key)
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
    """Punto de entrada de Lambda."""
    print("Evento recibido por Lambda:", json.dumps(event, indent=2))  # Imprime el evento completo
    
    with app.test_request_context(
        path=event.get('path', '/'),
        method=event.get('httpMethod', 'GET'),
        query_string=ImmutableMultiDict(event.get('queryStringParameters') or {})
    ):
        response = app.full_dispatch_request()
        print("Respuesta generada por Flask:", {
            "statusCode": response.status_code,
            "headers": dict(response.headers),
            "body": response.get_data(as_text=True)
        })  # Imprime la respuesta generada
        return {
            "statusCode": response.status_code,
            "headers": dict(response.headers),
            "body": response.get_data(as_text=True)
        }


if __name__ == '__main__':
    app.run(debug=True)
