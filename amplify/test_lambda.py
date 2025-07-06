import json
import pytest
import boto3
from moto import mock_dynamodb
from lambda_function import lambda_handler, UserService

@mock_dynamodb
class TestLambdaFunction:
    """
    Tests unitaires pour la fonction Lambda avec DynamoDB mocké
    """
    
    def setup_method(self):
        """
        Configuration avant chaque test
        """

        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        

        self.table = self.dynamodb.create_table(
            TableName='Users',
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        

        self.table.wait_until_exists()
        

        self.user_service = UserService(self.dynamodb)
    
    def test_add_user_success(self):
        """
        Test d'ajout d'utilisateur réussi
        """
        
        event = {
            'httpMethod': 'POST',
            'path': '/add_user',
            'body': json.dumps({
                'name': 'John Doe',
                'email': 'john@example.com',
                'age': 30
            })
        }
        
        
        response = lambda_handler(event, {})
        
        
        assert response['statusCode'] == 201
        body = json.loads(response['body'])
        assert body['message'] == 'Utilisateur créé avec succès'
        assert body['user']['name'] == 'John Doe'
        assert body['user']['email'] == 'john@example.com'
        assert body['user']['age'] == 30
        assert 'id' in body['user']
        assert 'created_at' in body['user']
