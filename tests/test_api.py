import requests
import json

def test_api():
    base_url = "http://localhost:4566"

    # 1. Test /camino_mas_largo
    response = requests.get(f"{base_url}/camino_mas_largo", params={"start": "the", "end": "for"})
    print("/camino_mas_largo Response:")
    print(response.status_code, response.json())

    # 2. Test /Dijkstra/
    response = requests.get(f"{base_url}/Dijkstra/", params={"start": "the", "target": "end"})
    print("/Dijkstra/ Response:")
    print(response.status_code, response.json())

    # 3. Test /nodos_aislados
    response = requests.get(f"{base_url}/nodos_aislados")
    print("/nodos_aislados Response:")
    print(response.status_code, response.json())

    # 4. Test /nodos_alto_grado
    response = requests.get(f"{base_url}/nodos_alto_grado", params={"umbral": 2})
    print("/nodos_alto_grado Response:")
    print(response.status_code, response.json())

    # 5. Test /nodos_grado_especifico
    response = requests.get(f"{base_url}/nodos_grado_especifico", params={"grado": 3})
    print("/nodos_grado_especifico Response:")
    print(response.status_code, response.json())


if __name__ == "__main__":
    test_api()
