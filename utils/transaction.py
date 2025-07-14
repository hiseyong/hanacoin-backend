from database.connection import get_connection
from typing import Optional


def record_transaction(sender_address: Optional[str], receiver_address: Optional[str], amount: float) -> None:
    """
    트랜잭션 기록 함수. 입금, 출금, 전송 모두 처리 가능.

    - 입금: sender_address = None
    - 출금: receiver_address = None
    - 전송: sender_address, receiver_address 모두 존재
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO transactions (sender_address, receiver_address, amount)
                VALUES (%s, %s, %s)
            """, (sender_address, receiver_address, amount))
            conn.commit()
    finally:
        conn.close()