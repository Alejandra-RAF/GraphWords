# tests/unit/test_create_api.py
import unittest
from src.utility_scripts.create_api import app

class TestCreateAPI(unittest.TestCase):
    def test_home_route(self):
        """Testea si la API responde correctamente en el endpoint principal"""
        tester = app.test_client()
        response = tester.get('/')
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
