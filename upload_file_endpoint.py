from flask import jsonify, request
from vault_utils import create_vault_client, kv_store
from flask import Blueprint

upload_file_endpoint = Blueprint('upload_file_endpoint', __name__)

@upload_file_endpoint.route('/vault/pgp/upload', methods=['POST'])
def upload_file():  
    if 'file' not in request.files:
        return 'Bad Request: No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'Bad Request: No selected file', 400
    if file:
        file_content = file.read()
        path = request.form.get('path')
        if not path:
            return 'Bad Request: Path is required', 400
        if not path.startswith('keys/') and not path.startswith('file/'):
            return 'Bad Request: Path must start with "keys/" or "file/"', 400
       
    client = create_vault_client()  
    try:
        client.secrets.kv.read_secret_version(
            mount_point=kv_store,
            path=path
        )
        return jsonify({"error": f"Secret already exists at this path: {path}"}), 400
    except hvac.exceptions.InvalidPath:
        pass
    client.secrets.kv.create_or_update_secret(
            mount_point=kv_store,
            path=path,
            secret={'file_content': file_content.decode()},
        )
    return jsonify({"success": f"UPLOADED PGP KEY, Path:{path}"}), 200
