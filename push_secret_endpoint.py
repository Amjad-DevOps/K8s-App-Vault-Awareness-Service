from flask import jsonify, request
from vault_utils import create_vault_client, kv_store
from flask import Blueprint
import hvac

push_secret_endpoint = Blueprint('push_secret_endpoint', __name__)

@push_secret_endpoint.route('/vault/push_secret', methods=['POST'])
def push_secret():
    key = request.json.get('key')
    value = request.json.get('value')
    path = request.json.get('path')
    if not key:
        return 'Bad Request: key is required', 400
    if not value:
        return 'Bad Request: value is required', 400
    if not path:
        return 'Bad Request: path is required', 400  
    if not path.startswith('credentials/'):
        return 'Bad Request: Path must start with "credentials"', 400
    client = create_vault_client()
    try:
        client.secrets.kv.read_secret_version(
            mount_point=kv_store,
            path=path
        )
        return jsonify({"error": f"Secret already exists at this path: {path}"}), 400
    except hvac.exceptions.InvalidPath:
        pass
   
    secret_data = {key: value}
    client.secrets.kv.create_or_update_secret(
        mount_point=kv_store,
        path=path,
        secret=secret_data,
    )
    return 'Secret pushed to Vault', 200
