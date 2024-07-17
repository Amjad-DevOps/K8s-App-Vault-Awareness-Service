# K8s-App-Vault-Awareness-Service
Vault awareness service is a Python code service that typically refers to the ability of a Python application or service to interact with HashiCorp's Vault to create, update, and read secrets from the vault server using APIs. 

Vault is a tool for securely accessing secrets, such as API keys, passwords, or certificates.

Let's create a vault service in Python and deploy it in Kubernetes.

Prerequisites: Kubernetes Cluster, Vault Server, GitLab CI/CD, Docker, Gloo Edge

API's:

1. /vault/aes/generate: Generate and store an AES key to the vault.
```
curl --location 'https://<address>/vault/aes/generate' \
--header 'Content-Type: application/json' \
--data '
{
    "vaultKeyDTO": {
         "name": "sample11"
}
}'
```

2. /vault/pgp/generate: Generate PGP public and private keys and securely store them in the vault.
```
curl --location 'https://<address>/vault/keys/pgp/generate' \
--header 'Content-Type: application/json' \
--data '{
    "vaultKeyDTO": {
        "PublicKeyFilePath": "file/<path>",
        "PublicKeyFileName": "pgp-public.gpg",
        "PrivateKeyFilePath": "file/<path>",
        "PrivateKeyFileName": "pgp-private.gpg",
        "passPhrase": "123abdc456dfg"
    }
}

```
3. /vault/pgp/upload: Upload the PGP file to the vault.
```
curl --location 'https://<address>/vault/pgp/upload' \
--form 'file=@"<location>/pgp-private.gpg"' \
--form 'path="<path>"'
```

4. /vault/read_secret : Read the secret from the vault
```
curl --location 'https://<address>/vault/read_secret' \
--header 'Content-Type: application/json' \
--data '{
    "path": "<path>"
}
'
```

5. /vault/push_secret : Push the secret to the vault
```
curl --location 'https://<address>/vault/push_secret' \
--header 'Content-Type: application/json' \
--data '{
    "path": "<path>",
    "key": "<key_name>,
    "value": "<value>"
}
'
```
