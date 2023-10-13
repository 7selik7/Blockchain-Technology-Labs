import hashlib
import json
import time


class SYO_Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.syo_create_genesis_block()

    def syo_create_genesis_block(self):
        previous_hash = hashlib.sha256("seliutin".encode()).hexdigest()
        genesis_proof = 23062004

        block = {
            'index': 1,
            'timestamp': time.time(),
            'transactions': [],
            'proof': genesis_proof,
            'previous_hash': previous_hash
        }

        self.chain.append(block)

    def syo_new_block(self, proof):
        previous_block = self.syo_last_block
        previous_hash = self.syo_hash(previous_block)

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash,
        }

        self.current_transactions = []
        self.chain.append(block)

        return block

    def syo_new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

    def syo_proof_of_work(self, last_proof):
        proof = 0
        while self.syo_valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def syo_valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash.endswith("2004")

    @staticmethod
    def syo_hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def syo_last_block(self):
        if self.chain:
            return self.chain[-1]
        else:
            return None


my_blockchain = SYO_Blockchain()

for _ in range(100):
    new_proof = my_blockchain.syo_proof_of_work(my_blockchain.syo_last_block['proof'])
    my_blockchain.syo_new_block(new_proof)
    print(_)

blockchain_data = my_blockchain.chain

with open("blockchain_data.json", "w") as json_file:
    json.dump(blockchain_data, json_file, indent=4)


