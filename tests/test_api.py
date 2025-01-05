import requests
import os

def test_api():
    api_url = os.getenv("API_URL")  # Ahora toma la URL pública expuesta por Ngrok
    if not api_url:
        raise ValueError("API_URL no está configurada")

    endpoints = [
        "/camino_mas_largo?start=the&end=for",
        "/Dijkstra/?start=the&target=for",
        "/nodos_aislados",
        "/nodos_alto_grado?umbral=3",
        "/nodos_grado_especifico?grado=2"
    ]

    for endpoint in endpoints:
        full_url = f"{api_url}{endpoint}"
        print(f"\nTesting endpoint: {full_url}")
        try:
            response = requests.get(full_url)
            print(f"Status Code: {response.status_code}")
            try:
                print("Response JSON:", response.json())
            except Exception:
                print("Non-JSON response:", response.text)

        except requests.exceptions.RequestException as e:
            print(f"Error during request to {endpoint}: {e}")

if __name__ == "__main__":
    test_api()
