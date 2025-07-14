from fastapi import APIRouter, Depends, HTTPException
from database.connection import get_connection
from auth.session import get_current_user

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

@router.get("/transactions")
async def get_transaction_history(user_id: int = Depends(get_current_user)):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 유저의 지갑 주소 조회
            cursor.execute("SELECT wallet_address FROM users WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="User not found")
            wallet_address = result["wallet_address"]

            # 입출금 내역 조회
            cursor.execute("""
                SELECT id, sender_address, receiver_address, amount, timestamp
                FROM transactions
                WHERE sender_address = %s OR receiver_address = %s
                ORDER BY timestamp DESC
            """, (wallet_address, wallet_address))

            transactions = cursor.fetchall()

        return {"wallet_address": wallet_address, "transactions": transactions}

    finally:
        conn.close()