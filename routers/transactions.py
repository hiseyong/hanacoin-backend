from fastapi import APIRouter, Depends, HTTPException
from auth.session import get_current_user
from database.transaction import get_wallet_address_by_user_id, get_transactions_by_wallet

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