import boto3
import json
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

app = Flask(__name__)

s3 = boto3.client('s3')  
bucket_input = "graph-generated-2025"

def seleccionar_archivo(type):
    archivos = {
        "3": "processed_palabras_3.txt",
        "4": "processed_palabras_4.txt",
        "5": "processed_palabras_5.txt"
    }
    return archivos.get(type, "processed_palabras_3.txt") 

@app.route('/Dijkstra/', methods=['GET'])
def api_dijkstra():
    try:
        type = request.args.get('type', "3")  # Si no se envía type, se asigna "3" por defecto.
        file_name = seleccionar_archivo(type)

        _, graph = leer_diccionario_desde_s3(bucket_input, file_name)

        start_word = request.args.get('start')
        end_word = request.args.get('end')

        if not start_word or not end_word:
            return jsonify({"message": "Faltan parámetros 'start' y/o 'end'"}), 400

        path, distance = dijkstra(graph, start_word, end_word)

        if distance < float('infinity'):
            return jsonify({
                "start": start_word,
                "end": end_word,
                "path": path,
                "distance": distance,
                "message": "Camino más corto encontrado"
            }), 200
        else:
            return jsonify({"message": f"No hay un camino entre '{start_word}' y '{end_word}'"}), 404
    except Exception as e:
        return jsonify({"message": f"Error en Dijkstra: {str(e)}"}), 500

@app.route('/camino_mas_largo', methods=['GET'])
def api_camino_mas_largo():
    try:
        type = request.args.get('type', "3")
        file_name = seleccionar_archivo(type)

        _, graph = leer_diccionario_desde_s3(bucket_input, file_name)

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
            max_path, max_distance, start_word, end_word = camino_mas_largo(graph)
            return jsonify({
                "start": start_word,
                "end": end_word,
                "path": max_path,
                "distance": max_distance,
                "message": "Camino más largo general calculado"
            }), 200
    except Exception as e:
        return jsonify({"message": f"Error en camino más largo: {str(e)}"}), 500

@app.route('/nodos_aislados', methods=['GET'])
def api_nodos_aislados():
    try:
        type = request.args.get('type', "3")
        file_name = seleccionar_archivo(type)

        _, graph = leer_diccionario_desde_s3(bucket_input, file_name)
        nodos_aislados = detectar_nodos_aislados(graph)

        return jsonify({
            "nodos_aislados": nodos_aislados,
            "message": "Nodos aislados identificados"
        }), 200
    except Exception as e:
        return jsonify({"message": f"Error en nodos aislados: {str(e)}"}), 500

@app.route('/nodos_alto_grado', methods=['GET'])
def api_nodos_alto_grado():
    try:
        type = request.args.get('type', "3")
        file_name = seleccionar_archivo(type)

        _, graph = leer_diccionario_desde_s3(bucket_input, file_name)
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
    try:
        type = request.args.get('type', "3")
        file_name = seleccionar_archivo(type)

        _, graph = leer_diccionario_desde_s3(bucket_input, file_name)
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

@app.route('/todos_los_caminos', methods=['GET'])
def api_todos_los_caminos():
    try:
        type = request.args.get('type', "3")
        file_name = seleccionar_archivo(type)

        _, graph = leer_diccionario_desde_s3(bucket_input, file_name)
        start_word = request.args.get('start')
        end_word = request.args.get('end')

        if not start_word or not end_word:
            return jsonify({"message": "Faltan parámetros 'start' y/o 'end'"}), 400

        all_paths = obtener_todos_los_caminos(graph, start_word, end_word)

        return jsonify({
            "start": start_word,
            "end": end_word,
            "all_paths": all_paths,
            "message": "Todos los caminos calculados"
        }), 200
    except Exception as e:
        return jsonify({"message": f"Error en todos los caminos: {str(e)}"}), 500

@app.route('/detectar_clusters', methods=['GET'])
def api_detectar_clusters():
    try:
        type = request.args.get('type', "3")
        file_name = seleccionar_archivo(type)

        _, graph = leer_diccionario_desde_s3(bucket_input, file_name)
        clusters = detectar_clusters(graph)

        return jsonify({
            "clusters": clusters,
            "message": "Clústeres identificados en el grafo"
        }), 200
    except Exception as e:
        return jsonify({"message": f"Error en detección de clústeres: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
