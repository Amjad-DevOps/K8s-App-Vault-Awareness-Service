from flask import Response
from vault_utils import create_vault_client
from flask import Blueprint

ready_endpoint = Blueprint('ready_endpoint', __name__)

@ready_endpoint.route('/vault/ready')
def ready():
    return Response("Ok Ready!", status=200)
