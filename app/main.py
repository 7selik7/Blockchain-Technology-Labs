import time
import uuid

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Query

from app.config import settings
from app.db.connection import get_db
from app.db.models import TransactionDB, BlockDB
from app.schemas.transaction_schema import Transaction
from sqlalchemy.orm import Session

from app.services.block_service import SYO_Blockchain

app = FastAPI(title="Lab2")


@app.get("/health", summary="Health check")
def health_check():
    return {
        "status": 200,
        "details": "working"
    }


@app.post("/transactions/new")
def create_transaction(transaction: Transaction, db: Session = Depends(get_db)):
    db_transaction = TransactionDB(
        sender=transaction.sender,
        recipient=transaction.recipient,
        amount=transaction.amount,
        id=str(uuid.uuid4()),
        timestamp=str(time.time()),
        is_in_block=False,
        fee=transaction.fee
    )

    try:
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding transaction to the database: {str(e)}")

    return {"message": "Transaction added to the pool", "transaction_id": db_transaction.id}


@app.post("/mine")
def mine_block(
        max_transactions: int = Query(default=1, description="Maximum number of transactions to mine"),
        db: Session = Depends(get_db)
):
    transactions = (
        db.query(TransactionDB)
        .filter(TransactionDB.is_in_block == False)
        .limit(max_transactions)
        .all()
    )

    if not transactions:
        raise HTTPException(status_code=400, detail="No transactions in the pool to mine")

    transactions_as_dicts = [transaction.to_dict() for transaction in transactions]
    total_fee = sum([transaction.fee for transaction in transactions])

    block = SYO_Blockchain(transactions_as_dicts, db)
    new_block = block.syo_new_block()

    for transaction in transactions:
        transaction.is_in_block = True
    db.commit()

    return {"message": "Block mined successfully", "block": new_block, "fee": total_fee}



@app.get("/chain")
def get_chain(db: Session = Depends(get_db)):
    blocks = (db.query(BlockDB).all())
    my_blockchain = [block.to_dict() for block in blocks]
    return {"chain": my_blockchain, "length": len(my_blockchain)}


if __name__ == '__main__':
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
