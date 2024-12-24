import unittest
from src.utility_scripts.create_api import app

class TestCreateAPI(unittest.TestCase):
    def test_root_endpoint(self):
        """Prueba que el endpoint raíz devuelva el código 200"""
        tester = app.test_client()
        response = tester.get("/")
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
