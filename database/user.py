from database.connection import get_connection
from database.wallet import create_wallet

def create_user(username, hashed_password, wallet_address, wallet_public_key):
    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO users (username, hashed_password, wallet_address, wallet_public_key)
            VALUES (%s, %s, %s, %s)
        """, (username, hashed_password, wallet_address, wallet_public_key))
        conn.commit()

        user_id = cursor.lastrowid
        create_wallet(user_id)

    conn.close()