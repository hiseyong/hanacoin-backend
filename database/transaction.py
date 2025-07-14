from database.connection import get_connection

def get_wallet_address_by_user_id(user_id: int) -> str:
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT wallet_address FROM users WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            if not result:
                return None
            return result["wallet_address"]
    finally:
        conn.close()


def get_transactions_by_wallet(wallet_address: str):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # wallet_address → user_id
            cursor.execute("""
                SELECT id FROM users WHERE wallet_address = %s
            """, (wallet_address,))
            user = cursor.fetchone()
            if not user:
                return []

            user_id = user["id"]

            # user_id → wallet.id
            cursor.execute("""
                SELECT id FROM wallets WHERE user_id = %s
            """, (user_id,))
            wallet = cursor.fetchone()
            if not wallet:
                return []

            wallet_id = wallet["id"]

            # 트랜잭션 조회
            cursor.execute("""
                SELECT 
                    t.id,
                    uw1.username AS sender,
                    uw2.username AS receiver,
                    t.amount,
                    t.tx_hash,
                    t.status,
                    t.created_at
                FROM transactions t
                LEFT JOIN wallets w1 ON t.sender_wallet_id = w1.id
                LEFT JOIN users uw1 ON w1.user_id = uw1.id
                LEFT JOIN wallets w2 ON t.receiver_wallet_id = w2.id
                LEFT JOIN users uw2 ON w2.user_id = uw2.id
                WHERE t.sender_wallet_id = %s OR t.receiver_wallet_id = %s
                ORDER BY t.created_at DESC
            """, (wallet_id, wallet_id))

            return cursor.fetchall()

    finally:
        conn.close()