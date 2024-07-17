from flask import Flask
from vault_utils import create_vault_client
from ready_endpoint import ready_endpoint
from aes_generate_endpoint import aes_generate_endpoint
from pgp_generate_endpoint import pgp_generate_endpoint
from upload_file_endpoint import upload_file_endpoint
from read_secret_endpoint import read_secret_endpoint
from push_secret_endpoint import push_secret_endpoint

app = Flask(__name__)

# Register blueprints
app.register_blueprint(ready_endpoint)
app.register_blueprint(aes_generate_endpoint)
app.register_blueprint(pgp_generate_endpoint)
app.register_blueprint(upload_file_endpoint)
app.register_blueprint(read_secret_endpoint)
app.register_blueprint(push_secret_endpoint)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
