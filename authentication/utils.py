import jwt
import requests
from jwt.algorithms import RSAAlgorithm
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings

import firebase_admin
from firebase_admin import credentials, auth

if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

def verify_firebase_token(id_token: str):
    """
    Verifies a Firebase ID token and returns the decoded data if valid.
    """
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token  # contains 'uid', 'email', etc.
    except Exception as e:
        print("Invalid Firebase token:", e)
        return None
    


def get_apple_public_key(kid):
    keys = requests.get(settings.APPLE_PUBLIC_KEYS_URL).json()["keys"]
    key = next((k for k in keys if k["kid"] == kid), None)
    if not key:
        raise ValueError("Invalid key ID")
    return RSAAlgorithm.from_jwk(key)


def verify_apple_token(identity_token):
    headers = jwt.get_unverified_header(identity_token)
    public_key = get_apple_public_key(headers["kid"])

    decoded = jwt.decode(
        identity_token,
        key=public_key,
        algorithms=["RS256"],
        audience=settings.APPLE_AUDIENCE,
        issuer="https://appleid.apple.com",
    )
    return decoded 




def verify_google_token(identity_token):
    """
    Verifies the Google identity token from Android or iOS.
    Returns decoded user info if valid, else None.
    """
    try:
        # Verify the token
        idinfo = id_token.verify_oauth2_token(identity_token, requests.Request())
        print(idinfo['aud'])
        # Check audience — must match your registered client IDs
        if idinfo["aud"] not in settings.GOOGLE_CLIENT_IDS:
            raise ValueError("Invalid audience.")
        # Optional: Verify the issuer
        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            print(idinfo["iss"])
            raise ValueError("Invalid issuer.")
        return idinfo
    except ValueError:
        return None
