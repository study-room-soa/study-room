import os
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = "HS256"
security = HTTPBearer(auto_error=False)

def current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(security)
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="missing_token"
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            options={
                "require": ["sub", "name", "iat", "exp"]
            }
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="token_expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="invalid_token"
        )