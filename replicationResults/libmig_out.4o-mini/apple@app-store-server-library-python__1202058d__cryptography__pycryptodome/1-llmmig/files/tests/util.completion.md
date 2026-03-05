### Explanation of Changes

To migrate the code from using the `cryptography` library to the `pycryptodome` library, the following changes were made:

1. **Key Generation and Serialization**: The `cryptography` library's methods for generating and serializing keys were replaced with equivalent methods from `pycryptodome`. Specifically, the `ec` module from `cryptography` was replaced with the `ECC` module from `pycryptodome`.

2. **JWT Encoding and Decoding**: The `jwt` library remains the same, but the way keys are handled has changed. The private and public keys are now generated and serialized using `pycryptodome` methods.

3. **Removed Unused Imports**: The import for `serialization` from `cryptography` was removed since it is no longer needed.

Here is the modified code:

```python
# Copyright (c) 2023 Apple Inc. Licensed under MIT License.

from typing import Any, Dict
import jwt
from jwt.api_jwt import decode_complete
import json
import os
from Crypto.PublicKey import ECC
from appstoreserverlibrary.models.Environment import Environment
from appstoreserverlibrary.signed_data_verifier import SignedDataVerifier

def create_signed_data_from_json(path: str) -> str:
    data = read_data_from_file(path)
    decoded_data = json.loads(data)
    private_key = ECC.generate(curve='P-256')
    private_key_pem = private_key.export_key(format='PEM').decode()
    return jwt.encode(payload=decoded_data, key=private_key_pem, algorithm='ES256')

def decode_json_from_signed_date(data: str) -> Dict[str, Any]:
    public_key = ECC.generate(curve='P-256').public_key()
    public_key_pem = public_key.export_key(format='PEM').decode()
    return decode_complete(jwt=data, key=public_key_pem, algorithms=['ES256'], options={"verify_signature": False})

def read_data_from_file(path: str) -> str:
    full_path = os.path.join(path)
    with open(full_path, mode='r') as test_file:
        return test_file.read()
    
def read_data_from_binary_file(path: str) -> str:
    full_path = os.path.join(path)
    with open(full_path, mode='rb') as test_file:
        return test_file.read()

def get_signed_data_verifier(env: Environment, bundle_id: str, app_apple_id: int = 1234) -> SignedDataVerifier:
    verifier = SignedDataVerifier([read_data_from_binary_file('tests/resources/certs/testCA.der')], False, env, bundle_id, app_apple_id)
    verifier._chain_verifier.enable_strict_checks = False # We don't have authority identifiers on test certs
    return verifier

def get_default_signed_data_verifier():
    return get_signed_data_verifier(Environment.LOCAL_TESTING, "com.example")
``` 

This code now uses `pycryptodome` for ECC key generation and serialization while maintaining the original structure and functionality of the code.