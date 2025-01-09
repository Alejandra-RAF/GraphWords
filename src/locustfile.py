import time
from locust import HttpUser, task, between

class GraphWordUser(HttpUser):
    wait_time = between(1, 5)  # Tiempo de espera aleatorio entre solicitudes

    @task
    def test_dijkstra_endpoint(self):
        """Prueba del endpoint de Dijkstra."""
        response = self.client.get("/Dijkstra/", params={
            "start": "not",
            "target": "can",
            "tipo": "3"
        })
        assert response.status_code == 200, f"Error en Dijkstra: {response.text}"
    
    @task
    def test_camino_mas_largo(self):
        """Prueba del endpoint de camino más largo."""
        response = self.client.get("/camino_mas_largo", params={
            "start": "well",
            "end": "role",
            "tipo": "4"
        })
        assert response.status_code == 200, f"Error en camino más largo: {response.text}"

    @task
    def test_nodos_aislados(self):
        """Prueba del endpoint de nodos aislados."""
        response = self.client.get("/nodos_aislados", params={"tipo": "3"})
        assert response.status_code == 200, f"Error en nodos aislados: {response.text}"

    @task
    def test_nodos_alto_grado(self):
        """Prueba del endpoint de nodos con alto grado de conectividad."""
        response = self.client.get("/nodos_alto_grado", params={"umbral": 2, "tipo": "3"})
        assert response.status_code == 200, f"Error en nodos alto grado: {response.text}"

    @task
    def test_nodos_grado_especifico(self):
        """Prueba del endpoint de nodos con un grado de conectividad específico."""
        response = self.client.get("/nodos_grado_especifico", params={"grado": 3, "tipo": "3"})
        assert response.status_code == 200, f"Error en nodos grado específico: {response.text}"

    @task
    def test_todos_los_caminos(self):
        """Prueba del endpoint de todos los caminos."""
        response = self.client.get("/todos_los_caminos", params={
            "start": "not",
            "target": "for",
            "tipo": "3"
        })
        assert response.status_code == 200, f"Error en todos los caminos: {response.text}"

    @task
    def test_detectar_clusters(self):
        """Prueba del endpoint de detección de clústeres."""
        response = self.client.get("/detectar_clusters", params={"tipo": "5"})
        assert response.status_code == 200, f"Error en detectar clústeres: {response.text}"
