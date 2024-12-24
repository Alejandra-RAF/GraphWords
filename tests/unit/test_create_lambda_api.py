import unittest
from src.lambdas.create_lambda_api import create_bucket

class TestCreateLambdaAPI(unittest.TestCase):
    def test_create_bucket(self):
        """Prueba si la función create_bucket maneja nombres correctamente"""
        result = create_bucket("test-bucket")
        self.assertIsNotNone(result)

if __name__ == "__main__":
    unittest.main()
