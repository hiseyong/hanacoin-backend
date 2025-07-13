from fastapi import APIRouter, HTTPException, status, Depends
from models.user import *
from database.connection import get_connection
from database.user import create_user
from utils.crypto import hash_password, verify_password
from utils.wallet import generate_wallet_keys
from auth.session import create_session_token, get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=SignupResponse)
async def signup(user: SignupRequest):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE username = %s", (user.username,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Username already taken")

            hashed_pw = hash_password(user.password)

            private_key, public_key, wallet_address = generate_wallet_keys()

            create_user(user.username, hashed_pw, wallet_address, public_key)

        return {
            "msg": "User created successfully",
            "private_key": private_key,
            "wallet_address": wallet_address,
            "wallet_public_key": public_key
        }
    finally:
        conn.close()


@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, hashed_password
                FROM users WHERE username = %s
            """, (data.username,))
            user = cursor.fetchone()

            if not user or not verify_password(data.password, user["hashed_password"]):
                raise HTTPException(status_code=401, detail="Invalid credentials")

            # 만료 없이 JWT 생성
            access_token = create_session_token(
                data={"sub": user["username"], "user_id": user["id"]}
            )

            # 세션 저장 (expires_at 없이)
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


@router.get("/userinfo", response_model=UserInfoResponse)
async def get_user_info(user_id: int = Depends(get_current_user)):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, wallet_address, wallet_public_key
                FROM users WHERE id = %s
            """, (user_id,))
            user = cursor.fetchone()

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

        return user  # dict와 유사한 row 객체가 반환됨

    finally:
        conn.close()