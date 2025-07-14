from database.connection import get_connection
import uuid
from decimal import Decimal
from typing import Optional, List, Dict

def get_wallet_address_by_user_id(user_id: int) -> Optional[str]:
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT wallet_address FROM users WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            return result["wallet_address"] if result else None
    finally:
        conn.close()


def get_transactions_by_wallet(wallet_address: str) -> List[Dict]:
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # wallet_address → user_id
            cursor.execute("SELECT id FROM users WHERE wallet_address = %s", (wallet_address,))
            user = cursor.fetchone()
            if not user:
                return []

            user_id = user["id"]

            # user_id → wallet.id
            cursor.execute("SELECT id FROM wallets WHERE user_id = %s", (user_id,))
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


def create_transaction(sender_wallet_id: int, receiver_wallet_id: int, amount: Decimal) -> str:
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            tx_hash = str(uuid.uuid4())  # 간단한 UUID 기반 트랜잭션 해시
            cursor.execute("""
                INSERT INTO transactions (
                    sender_wallet_id, receiver_wallet_id, amount, tx_hash, status
                ) VALUES (%s, %s, %s, %s, 'confirmed')
            """, (sender_wallet_id, receiver_wallet_id, amount, tx_hash))
            conn.commit()
            return tx_hash
    finally:
        conn.close()


def get_wallet_by_address(address: str) -> Optional[Dict]:
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT w.id, w.user_id, w.balance, u.username
                FROM wallets w
                JOIN users u ON w.user_id = u.id
                WHERE u.wallet_address = %s
            """, (address,))
            return cursor.fetchone()
    finally:
        conn.close()


def update_wallet_balance(wallet_id: int, delta: Decimal):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE wallets SET balance = balance + %s WHERE id = %s
            """, (delta, wallet_id))
            conn.commit()
    finally:
        conn.close()