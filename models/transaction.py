from pydantic import BaseModel

class TransactionRequest(BaseModel):
    receiver_address: str
    amount: float