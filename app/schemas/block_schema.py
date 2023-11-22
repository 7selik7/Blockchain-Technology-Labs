from typing import List
from pydantic import BaseModel
from app.schemas.transaction_schema import Transaction


class Block(BaseModel):
    index: int
    timestamp: float
    transactions: List[Transaction]
    proof: int
    previous_hash: str
