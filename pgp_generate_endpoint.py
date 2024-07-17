from flask import jsonify, request
from vault_utils import create_vault_client, kv_store
from flask import Blueprint
import gnupg

pgp_generate_endpoint = Blueprint('pgp_generate_endpoint', __name__)

@pgp_generate_endpoint.route('/vault/pgp/_generate', methods=['POST'])
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
