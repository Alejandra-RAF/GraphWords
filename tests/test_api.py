import os
import requests

def test_api():
    # Obtener URL de la API desde el entorno de GitHub Actions
    api_url = os.getenv("API_URL")
    if not api_url:
        raise ValueError("API_URL no está configurada")

    print(f"Usando API_URL: {api_url}")

    endpoints_with_payload = [
        {
            "endpoint": "test/camino_mas_largo",
            "payload": {
                "path": "/camino_mas_largo",
                "httpMethod": "ANY",
                "queryStringParameters": {
                    "start": "the",
                    "end": "for"
                }
            }
        },
        {
            "endpoint": "test/Dijkstra/",
            "payload": {
                "path": "/Dijkstra/",
                "httpMethod": "ANY",
                "queryStringParameters": {
                    "start": "the",
                    "target": "for"
                }
            }
        },
        {
            "endpoint": "test/nodos_aislados",
            "payload": {
                "path": "/nodos_aislados",
                "httpMethod": "ANY",
                "queryStringParameters": {}
            }
        },
        {
            "endpoint": "test/nodos_alto_grado",
            "payload": {
                "path": "/nodos_alto_grado",
                "httpMethod": "ANY",
                "queryStringParameters": {
                    "umbral": "3"
                }
            }
        },
        {
            "endpoint": "test/nodos_grado_especifico",
            "payload": {
                "path": "/nodos_grado_especifico",
                "httpMethod": "ANY",
                "queryStringParameters": {
                    "grado": "2"
                }
            }
        }
    ]

    for test in endpoints_with_payload:
        endpoint = test["endpoint"]
        payload = test["payload"]

        print(f"Testing endpoint: {endpoint}")
        try:
            response = requests.post(api_url, json=payload)
            print(f"Status Code: {response.status_code}")
            try:
                print(f"Response JSON: {response.json()}")
            except requests.exceptions.JSONDecodeError:
                print(f"Non-JSON response: {response.text}")
        except Exception as e:
            print(f"Error testing endpoint {endpoint}: {e}")

if __name__ == "__main__":
    test_api()
