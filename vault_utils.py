import hvac

kv_store = '<kv-store-name>'

def create_vault_client():
    # Taking keys from the mounted vault in the pod, so extracting keys from the vault location, instead can be provided directly but not recommended for prod env
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
