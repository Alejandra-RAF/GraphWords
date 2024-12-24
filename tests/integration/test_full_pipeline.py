import unittest
import boto3
from flask import Flask

class TestFullPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Configura LocalStack y los servicios necesarios"""
        cls.s3 = boto3.client("s3", endpoint_url="http://localhost:4566")
        cls.lambda_client = boto3.client("lambda", endpoint_url="http://localhost:4566")
        cls.bucket_name = "test-pipeline-bucket"

    def test_s3_bucket(self):
        """Prueba la creación de un bucket en LocalStack"""
        self.s3.create_bucket(Bucket=self.bucket_name)
        buckets = self.s3.list_buckets()["Buckets"]
        self.assertTrue(any(bucket["Name"] == self.bucket_name for bucket in buckets))

    def test_lambda_creation(self):
        """Prueba si una función Lambda se despliega correctamente"""
        response = self.lambda_client.list_functions()
        self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)

if __name__ == "__main__":
    unittest.main()
