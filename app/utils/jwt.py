from jose import jwt
from datetime import UTC, datetime, timedelta
from dotenv import load_dotenv
from config import secret_key, algorithm, token_expiry

load_dotenv()


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(UTC) + timedelta(minutes=float(token_expiry))

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, secret_key, algorithm=algorithm)

    

def decode_access_token(token):
    return jwt.decode(
        token.credentials,
        secret_key,
        algorithms=[algorithm]
    )
