from fastapi import APIRouter, Depends, HTTPException
from auth.session import get_current_user
from models.transaction import TransactionRequest
from database.transaction import get_wallet_address_by_user_id, get_transactions_by_wallet, create_transaction, update_wallet_balance, get_wallet_by_address
from decimal import Decimal

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

@router.get("/transactions")
async def get_transaction_history(current_user: int = Depends(get_current_user)):
    wallet_address = get_wallet_address_by_user_id(current_user['id'])
    if not wallet_address:
        raise HTTPException(status_code=404, detail="User not found")

    transactions = get_transactions_by_wallet(wallet_address)

    return {
        "wallet_address": wallet_address,
        "transactions": transactions
    }

@router.post("/send", response_model=dict)
async def send_transaction(
    data: TransactionRequest,
    current_user: dict = Depends(get_current_user)
):
    sender_wallet_address = get_wallet_address_by_user_id(current_user["id"])
    if not sender_wallet_address:
        raise HTTPException(status_code=404, detail="Sender wallet not found")

    sender_wallet = get_wallet_by_address(sender_wallet_address)
    receiver_wallet = get_wallet_by_address(data.receiver_address)

    if not receiver_wallet:
        raise HTTPException(status_code=404, detail="Receiver wallet not found")

    amount = Decimal(str(data.amount))
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    if sender_wallet["balance"] < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # 트랜잭션 생성
    tx_hash = create_transaction(sender_wallet["id"], receiver_wallet["id"], amount)

    # 잔고 업데이트
    update_wallet_balance(sender_wallet["id"], -amount)
    update_wallet_balance(receiver_wallet["id"], +amount)

    return {"msg": "Transaction successful", "tx_hash": tx_hash}