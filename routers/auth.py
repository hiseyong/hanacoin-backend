from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models.user import LoginResponse
from auth.session import create_session_token
from utils.crypto import verify_password
from database.connection import get_connection

router = APIRouter(tags=["Auth"])

@router.post("/token", response_model=LoginResponse)
async def login_with_oauth(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, hashed_password
                FROM users WHERE username = %s
            """, (form_data.username,))
            user = cursor.fetchone()

            if not user or not verify_password(form_data.password, user["hashed_password"]):
                raise HTTPException(status_code=401, detail="Invalid credentials")

            # 만료 없이 JWT 생성
            access_token = create_session_token(
                data={"sub": user["username"], "user_id": user["id"]}
            )

            cursor.execute("""
                INSERT INTO sessions (user_id, token)
                VALUES (%s, %s)
            """, (user["id"], access_token))
            conn.commit()

        return {
            "msg": "Login successful",
            "access_token": access_token,
            "token_type": "bearer"
        }

    finally:
        conn.close()