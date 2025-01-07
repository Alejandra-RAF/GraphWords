import boto3
from flask import Flask, request, jsonify
import heapq
from _collections import deque, defaultdict  
from _collections_abc import MutableSequence  

MutableSequence.register(deque)


def leer_diccionario_desde_s3(bucket_name, file_name):
    s3 = boto3.client('s3')

    try:
        content = s3.get_object(Bucket=bucket_name, Key=file_name)['Body'].read().decode('latin1', errors='replace')
    except Exception as e:
        print(f"Error al leer el archivo {file_name}: {e}")
        return None, None

    diccionario = {}
    for line in content.strip().split('\n'):
        try:
            palabra1, palabra2, peso = line.split()
            diccionario[(palabra1, palabra2)] = int(peso)
        except ValueError:
            print(f"Error al procesar la línea: {line}")

    graph = {}
    for (word1, word2), weight in diccionario.items():
        if word1 not in graph:
            graph[word1] = []
        if word2 not in graph:
            graph[word2] = []
        graph[word1].append((weight, word2))
        graph[word2].append((weight, word1))

    print("Diccionario de aristas:", diccionario)
    print("Grafo construido:", graph)
    return diccionario, graph

def dijkstra(graph, start, target):
    distances = {word: float('infinity') for word in graph}
    distances[start] = 0
    priority_queue = [(0, start)]
    previous_nodes = {start: None}

    while priority_queue:
        current_distance, current_word = heapq.heappop(priority_queue)

        if current_distance > distances[current_word]:
            continue

        for weight, neighbor in graph[current_word]:  
            distance = current_distance + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_word
                heapq.heappush(priority_queue, (distance, neighbor))

    path = []
    current_node = target
    while current_node is not None:
        path.append(current_node)
        current_node = previous_nodes.get(current_node)
    path.reverse()

    return path, distances[target]


def camino_mas_largo(graph, start=None, end=None):
    if start is not None and end is not None:
        return dijkstra(graph, start, end)

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

def detectar_nodos_aislados(graph):
    nodos_aislados = []
    for nodo, conexiones in graph.items():
        if all(conexion[0] == 0 for conexion in conexiones):
            nodos_aislados.append(nodo)
    return nodos_aislados

def obtener_todos_los_caminos(graph, start, target, max_depth=10):
    paths = []
    queue = deque([(start, [start])])

    while queue:
        current_node, path = queue.popleft()

        if len(path) > max_depth: 
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
            for weight, neighbor in graph[node]:  
                dfs(neighbor, cluster)

    for node in graph:
        if node not in visited:
            cluster = []
            dfs(node, cluster)
            if len(cluster) > 1: 
                clusters.append(cluster)

    return clusters

class Conectividad:
    def __init__(self, graph):
        self.graph = graph
    
    def contar_conexiones(self, palabra):
        if palabra in self.graph:
            return len(self.graph[palabra])
        return 0

    def nodos_alto_grado(self, umbral=0):
        nodos_con_alto_grado = {}
        for nodo in self.graph:
            grado = self.contar_conexiones(nodo)
            if grado >= umbral:
                nodos_con_alto_grado[nodo] = grado
        return nodos_con_alto_grado

    def nodos_con_grado_especifico(self, grado_deseado):
        nodos_con_grado_especifico = {}
        for nodo in self.graph:
            grado = self.contar_conexiones(nodo)
            if grado == grado_deseado:
                nodos_con_grado_especifico[nodo] = grado
        return nodos_con_grado_especifico
