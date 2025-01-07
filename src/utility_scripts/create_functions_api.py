import boto3
from flask import Flask, request, jsonify
import heapq
from collections import deque

# Obtener el nombre del archivo en S3
def obtener_nombre_archivo_en_s3(bucket_name, prefix):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    if 'Contents' in response and len(response['Contents']) > 1:
        return response['Contents'][3]['Key']
    return None

# Función para leer el archivo de aristas desde S3
def leer_diccionario_desde_s3(bucket_name, input_key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=input_key)
    content = response['Body'].read().decode('latin1', errors='replace')
    
    diccionario = {}
    for line in content.strip().split('\n'):
        try:
            palabra1, palabra2, peso = line.split()
            diccionario[(palabra1, palabra2)] = int(peso)
        except ValueError:
            print(f"Error al procesar la línea: {line}")
    
    # Crear el grafo aquí
    graph = {}
    for (word1, word2), weight in diccionario.items():
        if word1 not in graph:
            graph[word1] = []
        if word2 not in graph:
            graph[word2] = []
        graph[word1].append((weight, word2))
        graph[word2].append((weight, word1))
        
    return diccionario, graph

# Algoritmo de Dijkstra
def dijkstra(graph, start, target):
    # Inicialización
    distances = {word: float('infinity') for word in graph}
    distances[start] = 0
    priority_queue = [(0, start)]
    previous_nodes = {start: None}

    while priority_queue:
        current_distance, current_word = heapq.heappop(priority_queue)

        if current_distance > distances[current_word]:
            continue

        for weight, neighbor in graph[current_word]:  # Cambiado diccionario a graph
            distance = current_distance + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_word
                heapq.heappush(priority_queue, (distance, neighbor))

    # Reconstruir el camino
    path = []
    current_node = target
    while current_node is not None:
        path.append(current_node)
        current_node = previous_nodes.get(current_node)
    path.reverse()

    return path, distances[target]


# Función para encontrar el camino más largo en el grafo
def camino_mas_largo(graph, start=None, end=None):
    if start is not None and end is not None:
        return dijkstra(graph, start, end)

    # Buscar el camino más largo entre todos los pares de nodos
    max_distance = 0
    max_path = []
    start_word = ''
    target_word = ''

    for start in graph.keys():
        for end in graph.keys():
            if start != end:
                path, distance = dijkstra(graph, start, end)
                if distance < float('infinity') and distance > max_distance:
                    max_distance = distance
                    max_path = path
                    start_word = start
                    target_word = end

    return max_path, max_distance, start_word, target_word

def obtener_todos_los_caminos(graph, start, target, max_depth=10):
    paths = []
    queue = deque([(start, [start])])

    while queue:
        current_node, path = queue.popleft()

        if len(path) > max_depth:  # Limitar la profundidad
            continue

        for weight, neighbor in graph[current_node]:
            if neighbor in path:
                continue
            new_path = path + [neighbor]
            if neighbor == target:
                paths.append(new_path)
            else:
                queue.append((neighbor, new_path))

    return paths


def detectar_clusters(graph):
    visited = set()
    clusters = []

    def dfs(node, cluster):
        if node not in visited:
            visited.add(node)
            cluster.append(node)
            for weight, neighbor in graph[node]:  # Desempaquetamos el peso y el vecino
                dfs(neighbor, cluster)

    for node in graph:
        if node not in visited:
            cluster = []
            dfs(node, cluster)
            if len(cluster) > 1:  # Solo consideramos clusters con más de un nodo
                clusters.append(cluster)

    return clusters


# Función para detectar nodos aislados
def detectar_nodos_aislados(graph):
    nodos_aislados = []
    for nodo, conexiones in graph.items():
        # Verificar si todas las conexiones tienen peso 0 (posición[3] = 0)
        if all(conexion[0] == 0 for conexion in conexiones):
            nodos_aislados.append(nodo)
    return nodos_aislados


class Conectividad:
    def __init__(self, graph):
        self.graph = graph
    
    # Función para contar cuántas conexiones tiene una palabra
    def contar_conexiones(self, palabra):
        if palabra in self.graph:
            return len(self.graph[palabra])
        return 0

    # Función para identificar nodos con alto grado de conectividad
    def nodos_alto_grado(self, umbral=0):
        nodos_con_alto_grado = {}
        for nodo in self.graph:
            grado = self.contar_conexiones(nodo)
            if grado >= umbral:
                nodos_con_alto_grado[nodo] = grado
        return nodos_con_alto_grado

    # Función para seleccionar nodos con un grado de conectividad específico
    def nodos_con_grado_especifico(self, grado_deseado):
        nodos_con_grado_especifico = {}
        for nodo in self.graph:
            grado = self.contar_conexiones(nodo)
            if grado == grado_deseado:
                nodos_con_grado_especifico[nodo] = grado
        return nodos_con_grado_especifico
