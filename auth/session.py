from fastapi import Depends, HTTPException, Request, status
from jose import jwt, JWTError
from database.connection import get_connection
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_session_token(data: dict):
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_token_from_header(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or malformed")
    return auth_header[7:]

def get_current_user(request: Request):
    token = get_token_from_header(request)

    # 디코딩 시도
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token verification failed")

    # 세션 DB에서 토큰 유효성 확인
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM sessions WHERE user_id = %s AND token = %s", (user_id, token))
            session = cursor.fetchone()
            if not session:
                raise HTTPException(status_code=401, detail="Session not found or expired")
    finally:
        conn.close()

    return user_id  # 또는 사용자 정보 전체 반환도 가능