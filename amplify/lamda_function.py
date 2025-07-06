import json
import boto3
import uuid
from datetime import datetime
from decimal import Decimal


dynamodb = boto3.resource('dynamodb')
table_name = 'Users'

def lambda_handler(event, context):
    """
    Fonction Lambda pour gérer les opérations CRUD sur les utilisateurs
    """
    try:

        table = dynamodb.Table(table_name)
        

        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        
        if http_method == 'POST' and 'add_user' in path:
            return add_user(event, table)
        elif http_method == 'GET' and 'get_user' in path:
            return get_user(event, table)
        else:
            return create_response(400, {'error': 'Action non supportée'})
            
    except Exception as e:
        return create_response(500, {'error': str(e)})

def add_user(event, table):
    """
    Ajoute un nouvel utilisateur dans DynamoDB
    """
    try:
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        

        if not body.get('name') or not body.get('email'):
            return create_response(400, {'error': 'Nom et email requis'})
        

        user_id = str(uuid.uuid4())
        user_data = {
            'id': user_id,
            'name': body['name'],
            'email': body['email'],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        

        if body.get('age'):
            user_data['age'] = int(body['age'])
        

        table.put_item(Item=user_data)
        
        return create_response(201, {
            'message': 'Utilisateur créé avec succès',
            'user': user_data
        })
        
    except Exception as e:
        return create_response(500, {'error': f'Erreur lors de la création: {str(e)}'})

def get_user(event, table):
    """
    Récupère un utilisateur par son ID
    """
    try:
        user_id = event.get('pathParameters', {}).get('id')
        if not user_id:
            user_id = event.get('queryStringParameters', {}).get('id')
        
        if not user_id:
            return create_response(400, {'error': 'ID utilisateur requis'})
        

        response = table.get_item(Key={'id': user_id})
        
        if 'Item' not in response:
            return create_response(404, {'error': 'Utilisateur non trouvé'})
        
        user = json.loads(json.dumps(response['Item'], default=decimal_default))
        
