from database.connection import get_connection

def create_wallet(user_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO wallets (user_id, balance) VALUES (%s, %s)",
                (user_id, 0.0)
            )
            conn.commit()
    finally:
        conn.close()