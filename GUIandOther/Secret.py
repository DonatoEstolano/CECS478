import os
import json
import base64

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding as textPadding
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes, hmac

def Encrypter(message, pemFilePath):
    IV = os.urandom(16) # Creates an initialization vector of 16 bytes

    # Using the pem file path, loads the public key
    with open(pemFilePath, "rb") as pemFile:
        publicKey = serialization.load_pem_public_key(
            pemFile.read(),
            backend=default_backend()
        )

    AESKey = os.urandom(32) # Creates a key of 32 bytes to be used for encryption
    HMACKey = os.urandom(32) # Creates a key of 32 bytes for HMAC

    # Properly applies padding to the message in case it is too long/short for the block
    padder = textPadding.PKCS7(128).padder()
    paddedData = padder.update(message)
    paddedData += padder.finalize()

    # Encrypts the padded message
    cipher = Cipher(algorithms.AES(AESKey), modes.CBC(IV), backend=default_backend())
    encrypter = cipher.encryptor()
    ciphertext = encrypter.update(paddedData) + encrypter.finalize()

    # Creates a HMAC tag
    hmacTag = hmac.HMAC(HMACKey, hashes.SHA256(), backend=default_backend())
    hmacTag.update(ciphertext)

    CombinedKeys = AESKey + HMACKey # Concatenates the AES key and HMAC key

    # Encrypts the concatenated keys using the RSA object
    encryptedKeys = publicKey.encrypt(
        CombinedKeys,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Encodes the ciphertext, encrypted keys, and HMAC tag into JSON serializable format
    btsCiphertext = base64.encodebytes(ciphertext)
    encodedCiphertext = btsCiphertext.decode('ascii')
    btsEncryptedKeys = base64.encodebytes(encryptedKeys)
    encodedEncryptedKeys = btsEncryptedKeys.decode('ascii')
    btsHMACTag = base64.encodebytes(hmacTag.finalize())
    encodedHMACTag = btsHMACTag.decode('ascii')
    btsIV = base64.encodebytes(IV)
    encodedIV = btsIV.decode('ascii')

    # Puts information above into a JSON object
    #jsonObject = { "RSA Ciphertext" : encodedEncryptedKeys, "AES Ciphertext" : encodedCiphertext, "HMAC Tag" : encodedHMACTag, "IV" : encodedIV }
    #JSONFile = json.dumps(jsonObject)

    #return JSONFile
    return encodedCiphertext, encodedEncryptedKeys, encodedHMACTag, encodedIV

def Decrypter(JSONFile, privatePem):
    JSONObject = JSONFile # Loads the JSON key-value pairs in a variable

    # Puts each value of each key in a variable to be used later
    stbCiphertext = JSONObject['message'].encode('ascii')
    decodedCiphertext = base64.decodebytes(stbCiphertext)
    stbEncryptedKeys = JSONObject['keys'].encode('ascii')
    decodedEncryptedKeys = base64.decodebytes(stbEncryptedKeys)
    stbHMACTag = JSONObject['tag'].encode('ascii')
    decodedHMACTag = base64.decodebytes(stbHMACTag)
    stbIV = JSONObject['iv'].encode('ascii')
    decodedIV = base64.decodebytes(stbIV)

    # Using the pem file path, loads the private key
    with open(privatePem, "rb") as pemFile:
        privateKey = serialization.load_pem_private_key(
            pemFile.read(),
            password=b"test",
            backend=default_backend()
        )

    # Decrypts the concatenated keys using the private pem file
    DecryptedKeys = privateKey.decrypt(
        decodedEncryptedKeys,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Split the concatenated key into two (AES and HMAC)
    DecryptedAESKey = DecryptedKeys[:32]
    DecryptedHMACKey = DecryptedKeys[32:64]

    # Creates a HMAC tag
    hmacTag = hmac.HMAC(DecryptedHMACKey, hashes.SHA256(), backend=default_backend())
    hmacTag.update(decodedCiphertext)

    hmacTag.verify(decodedHMACTag) # Checks if the generated HMAC Tag matches the one from JSON

    # Decrypts the padded message
    cipher = Cipher(algorithms.AES(DecryptedAESKey), modes.CBC(decodedIV), backend=default_backend())
    decrypter = cipher.decryptor()
    plaintext = decrypter.update(decodedCiphertext) + decrypter.finalize()

    # Unpads the plaintext to its original version
    unpadder = textPadding.PKCS7(128).unpadder()
    originalMessage = unpadder.update(plaintext)
    originalMessage += unpadder.finalize()

    return originalMessage

def main():
    # The following commands were used in the terminal to generate the private-public 2048 RSA key pairs before this program is executed:
    # openssl genrsa -des3 -out private.pem 2048
    # openssl rsa -in private.pem -outform PEM -pubout -out public.pem

    pemFilePath = "/Users/estolanod/Desktop/public.pem" # File path to the public pem file
    privateFilePath = "/Users/estolanod/Desktop/private.pem" # File path to the private pem file path
    message = b"The nuclear code is DH37HF3978D7DKAWJEH, Mr. President" # Message to be encrypted then decrypted

    publicExists = os.path.isfile(pemFilePath)
    privateExists = os.path.isfile(privateFilePath)

    if publicExists:
        json = Encrypter(message, pemFilePath) # JSON object holding a returned JSON object holding sensitive information

        print("The original message is: ", message, "\n")
        print("After going through encryption, here is the JSON object:\n", json, "\n")
    else:
        print("Sorry, that file does not exist in the specified file path.")

    if privateExists:
        print("The decrypted message is: ", Decrypter(json, privateFilePath), "\n")
    else:
        print("Sorry, that file does not exist in the specified file path.")