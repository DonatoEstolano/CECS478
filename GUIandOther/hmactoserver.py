import json
import requests
import hashlib
import base64
import bcrypt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac

def response(password, salt, challenge):
    key = bcrypt.hashpw(password.encode('utf-8'), salt.encode('utf-8'))

    h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
    enchallenge = challenge.encode('utf-8')
    h.update(enchallenge)
    response = h.finalize()

    decodedresponse = base64.encodebytes(response).decode('utf-8')
    decodedresponse = decodedresponse.replace('\n', '')

    return decodedresponse