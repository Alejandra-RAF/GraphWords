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
            "endpoint": "/camino_mas_largo",
            "payload": {
                "path": "/camino_mas_largo",
                "httpMethod": "GET",
                "queryStringParameters": {
                    "start": "the",
                    "end": "for"
                }
            }
        },
        {
            "endpoint": "/Dijkstra/",
            "payload": {
                "path": "/Dijkstra/",
                "httpMethod": "GET",
                "queryStringParameters": {
                    "start": "the",
                    "target": "for"
                }
            }
        },
        {
            "endpoint": "/nodos_aislados",
            "payload": {
                "path": "/nodos_aislados",
                "httpMethod": "GET",
                "queryStringParameters": {}
            }
        },
        {
            "endpoint": "/nodos_alto_grado",
            "payload": {
                "path": "/nodos_alto_grado",
                "httpMethod": "GET",
                "queryStringParameters": {
                    "umbral": "3"
                }
            }
        },
        {
            "endpoint": "/nodos_grado_especifico",
            "payload": {
                "path": "/nodos_grado_especifico",
                "httpMethod": "GET",
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
