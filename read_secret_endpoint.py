from flask import jsonify, request
from vault_utils import create_vault_client, kv_store
from flask import Blueprint
import hvac

read_secret_endpoint = Blueprint('read_secret_endpoint', __name__)

@read_secret_endpoint.route('/vault/read_secret', methods=['POST'])
def read_secret():
    path = request.json.get('path')
    if not path:
        return 'Bad Request: path is required', 400  
    client = create_vault_client()
    try:
        secret_version_response = client.secrets.kv.read_secret_version(mount_point=kv_store, path=path)
    except hvac.exceptions.InvalidPath:
        return 'Secret not found at this path', 404
    secret_data = secret_version_response['data']['data']
    return jsonify(secret_data), 200
