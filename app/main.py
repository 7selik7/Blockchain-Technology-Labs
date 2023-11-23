import hashlib
import json
import time
import uuid
from typing import List

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


import requests
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import desc

from app.config import settings
from app.db.connection import get_db
from app.db.models import TransactionDB, BlockDB, NodeDB
from app.schemas.transaction_schema import Transaction
from sqlalchemy.orm import Session

from app.services.block_service import SYO_Blockchain

app = FastAPI(title="Lab2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    blocks = db.query(BlockDB).order_by(desc(BlockDB.timestamp)).all()
    my_blockchain = [block.to_dict() for block in blocks]
    return {"chain": my_blockchain, "length": len(my_blockchain)}


@app.post("/nodes/register")
def create_nodes(node_urls: List[str], db: Session = Depends(get_db)):
    added_nodes = []

    for node_url in node_urls:
        existing_node = db.query(NodeDB).filter(NodeDB.url == node_url).first()

        if not existing_node:
            new_node = NodeDB(id=str(uuid.uuid4()), url=node_url)
            db.add(new_node)
            db.commit()
            added_nodes.append({"node_id": new_node.id, "node_url": new_node.url})
        else:
            added_nodes.append({"message": f"Node with URL '{node_url}' already exists"})

    return {"message": "Nodes added successfully", "added_nodes": added_nodes}


@app.post("/nodes/resolve")
def resolve_nodes(db: Session = Depends(get_db)):
    current_block_chain = len(db.query(BlockDB).all())

    nodes = db.query(NodeDB).filter(NodeDB.url.notilike(f"%:{settings.PORT}%")).all()
    print(nodes[0].__dict__)
    longest_chain_url = None

    for node in nodes:
        chain_url = f"http://localhost:5000/chain"
        print(chain_url)

        chain_url = f"http://localhost:5000/chain"

        response = requests.get(chain_url)


        print(response)
        if response.status_code == 200:
            chain_length = response.json().get("length", 0)
            if chain_length > current_block_chain:
                chain = response.json().get("chain", [])
                if chain and validate_blocks(chain):
                    longest_chain_url = node.url

    if longest_chain_url:
        return {"message": f"Longest chain found at {longest_chain_url}"}
    else:
        return {"message": "No valid chains found"}


def validate_blocks(chain: list):
    current_block = chain[0]
    current_index = 1
    while current_index < len(chain):
        block = chain[current_index]
        block_string = json.dumps(block, sort_keys=True).encode()
        if current_block['previous_hash'] != hashlib.sha256(block_string).hexdigest():
            return False
        else:
            current_block = block
            current_index += 1
    return True


if __name__ == '__main__':
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
