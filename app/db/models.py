from sqlalchemy import Column, DateTime, String, BigInteger, JSON, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()


class BlockDB(Base):
    __tablename__ = "blocks"

    id = Column(String, primary_key=True)
    timestamp = Column(String)
    transactions = Column(JSON)
    proof = Column(BigInteger)
    previous_hash = Column(String)

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'proof': self.proof,
            'previous_hash': self.previous_hash
        }


class TransactionDB(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True)
    sender = Column(String)
    recipient = Column(String)
    amount = Column(Float)
    fee = Column(Float)
    timestamp = Column(String)
    is_in_block = Column(Boolean, default=False)

    def to_dict(self):
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount
        }
