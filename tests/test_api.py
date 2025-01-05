import requests
import os

def test_api():
    endpoints = [
        "/camino_mas_largo?start=the&end=for",
        "/Dijkstra/?start=the&target=for",
        "/nodos_aislados",
        "/nodos_alto_grado?umbral=3",
        "/nodos_grado_especifico?grado=2"
    ]
    
    # Obtener la URL de la API desde la variable de entorno
    api_url = os.getenv("API_URL", "http://172.17.0.2:4566")  # Default a localhost si no se configura
    
    if not api_url:
        print("Error: No se ha definido la variable de entorno 'API_URL'.")
        return

    print(f"Usando API_URL: {api_url}")

    for endpoint in endpoints:
        print(f"\nTesting endpoint: {endpoint}")
        try:
            response = requests.get(f"{api_url}{endpoint}")
            print(f"Status Code: {response.status_code}")

            try:
                json_data = response.json()
                print("Response JSON:", json_data)
            except requests.exceptions.JSONDecodeError:
                print("Non-JSON response:", response.text)

        except requests.exceptions.RequestException as e:
            print(f"Error during request to {endpoint}: {e}")

if __name__ == "__main__":
    test_api()
