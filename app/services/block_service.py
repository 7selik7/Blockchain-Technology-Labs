import hashlib
import json
import time
import uuid
from sqlalchemy import desc
from app.db.models import BlockDB


class SYO_Blockchain:
    def __init__(self, transactions, db_session):
        self.db_session = db_session
        self.transactions = transactions

    def syo_new_block(self):
        previous_block = self.syo_last_block
        previous_block = previous_block.__dict__
        previous_block.pop("_sa_instance_state", None)
        # previous_block = self.block_db_to_dict(previous_block)
        print("PREVIOS BLOCK", previous_block)
        print(type(previous_block))
        previous_hash = self.syo_hash(previous_block)

        block = self.syo_proof_of_work(previous_hash)

        block_instance = BlockDB(**block)
        self.db_session.add(block_instance)
        self.db_session.commit()

        return block

    def syo_proof_of_work(self, previous_hash):
        proof = 0
        while True:
            new_block = self.syo_find_block(proof, previous_hash)
            if new_block:
                return new_block
            proof += 1

    def syo_find_block(self, proof, previous_hash):
        block = {
            'id': str(uuid.uuid4()),
            'timestamp': str(time.time()),
            'transactions': self.transactions,
            'proof': proof,
            'previous_hash': previous_hash,
        }
        guess_hash = self.syo_hash(block)
        return block if guess_hash[-4:] == "2004" else None

    @staticmethod
    def syo_hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def syo_last_block(self):
        return self.db_session.query(BlockDB).order_by(desc(BlockDB.timestamp)).first()

    # @staticmethod
    # def block_db_to_dict(block_db):
    #     block_dict = block_db.__dict__.copy()
    #
    #     block_dict.pop("_sa_instance_state", None)
    #
    #     for key, value in block_dict.items():
    #         print(key, type(value), isinstance(value, datetime))
    #         if isinstance(value, datetime):
    #             block_dict[key] = value.strftime("%Y-%m-%d %H:%M:%S")
    #         elif isinstance(value, uuid.UUID):
    #             block_dict[key] = str(value)
    #
    #     return block_dict
