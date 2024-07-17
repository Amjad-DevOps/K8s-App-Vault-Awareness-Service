from flask import jsonify, request
from vault_utils import create_vault_client, kv_store
from flask import Blueprint
import secrets
import base64

aes_generate_endpoint = Blueprint('aes_generate_endpoint', __name__)

@aes_generate_endpoint.route('/vault/aes/generate', methods=['POST'])
def aes_generate():
    data = request.get_json()
    vaultKeyDTO = data.get('vaultKeyDTO')
    if vaultKeyDTO is not None:
        key_name = vaultKeyDTO.get('key_name')
        if not key_name:
            return 'Bad Request: key_name is required', 400
       
        aes_key = secrets.token_bytes(32)
        encoded_key = base64.b64encode(aes_key)
        decoded_key = encoded_key.decode()
   
    path = f'keys/AES/'
   
    client = create_vault_client()
    try:
        client.secrets.kv.read_secret_version(
            mount_point=kv_store,
            path=path
        )
        return jsonify({"error": f"Secret already exists at this path: {path}"}), 400
    except hvac.exceptions.InvalidPath:
        pass
    secret_data = {name: decoded_key}
    client.secrets.kv.create_or_update_secret(
        mount_point=kv_store,
        path=path,
        secret=secret_data,
    )
   
    return jsonify({"success": f"GENERATED AES KEY, Path: {path}"}), 200
