from flask import Flask, jsonify, request, Response
import hvac
import os
import secrets
import base64
import gnupg

app = Flask(__name__)

# Global Variables
kv_store = '<kv-store-name>'

# Function to create a vault client
def create_vault_client():
    # Taking keys from the mounted vault in the pod, so extracting keys from the vault location, instead can provide directly but not recommeded for prod env
    # with open('/root/credentials/vault.api.url', 'r') as f:
    #     vault_addr = f.read().strip()
    # with open('/root/credentials/vault.api.token', 'r') as f:
    #     vault_token = f.read().strip()
    vault_addr = '<VAULT_ADDRESS>'
    vault_token = '<VAULT_TOKEN>'
    client = hvac.Client(
        url=vault_addr,
        token=vault_token,
        verify=False,
    )    
    return client


# Function to check if the vault is ready
@app.route('/vault/ready')
def ready():
    return Response("Ok Ready!", status=200)


# Function to generate aes key and store in vault
@app.route('/vault/aes/generate', methods=['POST'])
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


# Function to generate pgp key and store in vault
@app.route('/vault/pgp/_generate', methods=['POST'])
def pgp_generate():
    data = request.get_json()
    vaultKeyDTO = data.get('vaultKeyDTO')
    if vaultKeyDTO is not None:      
        name = vaultKeyDTO.get('name')
        privateKeyName = vaultKeyDTO.get('privateKeyName')
        privateKeyPath = vaultKeyDTO.get('privateKeyPath')
        publicKeyName = vaultKeyDTO.get('publicKeyName')
        publicKeyPath = vaultKeyDTO.get('publicKeyPath')
        passPhrase = vaultKeyDTO.get('passPhrase')
        if not privateKeyName:
            return 'Bad Request: privateKeyName is required', 400
        if not privateKeyPath:
            return 'Bad Request: privateKeyPath is required', 400
        if not publicKeyName:
            return 'Bad Request: publicKeyName is required', 400
        if not publicKeyPath:
            return 'Bad Request: publicKeyPath is required', 400
        if not passPhrase:
            return 'Bad Request: passphrase is required', 400
        if not privateKeyPath.startswith('keys/') and not privateKeyPath.startswith('file/'):
            return 'Bad Request: Private Key Path must start with "keys/" or "file/"', 400
        if not publicKeyPath.startswith('keys/') and not publicKeyPath.startswith('file/'):
            return 'Bad Request: Public Key Path must start with "keys/" or "file/"', 400
       
    gpg = gnupg.GPG()  
    key_data = gpg.gen_key_input(
        passphrase=passPhrase,
        )
    key = gpg.gen_key(key_data)
    pgp_public_keys = str(gpg.export_keys(key.fingerprint))
    pgp_private_keys = str(gpg.export_keys(key.fingerprint, True, passphrase=passPhrase))
    client = create_vault_client()
    paths = [privateKeyPath, publicKeyPath]  
    for path in paths:
        try:
            client.secrets.kv.read_secret_version(
            mount_point=kv_store,
            path=path
            )
            return jsonify({"error": f"Secret already exists at this path: {path}"}), 400
        except hvac.exceptions.InvalidPath:
            pass
   
    secrets = {
    publicKeyPath: {publicKeyName: pgp_public_keys},
    privateKeyPath: {privateKeyName: pgp_private_keys},
    }
    for path, secret_data in secrets.items():
        client.secrets.kv.create_or_update_secret(
            mount_point=kv_store,
            path=path,
            secret=secret_data,
        )
    return jsonify({"success": f"UPLOADED PGP KEY, key:{key}"}), 200


# Function to upload pgp key to vault using file as input
@app.route('/vault/pgp/upload', methods=['POST'])
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


# Function to read secret from vault
@app.route('/vault/read_secret', methods=['POST'])
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


# Function to push secret to vault
@app.route('/vault/push_secret', methods=['POST'])
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
