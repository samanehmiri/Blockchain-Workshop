# Importing libraries
import datetime
import hashlib
import json
import pickle, bz2
from flask import Flask, jsonify

class Blockchain:

    def __init__(self):
        # Blockchain initialization
        self.chain = []

        _, genesis_block = self.proof_of_work()
        self.add_block(genesis_block, skip_return=True)

        self.backup_chain()

    def add_block(self, block, skip_return=False):
        self.chain.append(block)
        self.backup_chain()

        if skip_return is False:
            return block

    
    def prepare_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
        return block

    
    def backup_chain(self):
        sfile = bz2.BZ2File('chain_bk','w')
        pickle.dump(self.chain, sfile)

    
    def load_chain(self):
        sfile = bz2.BZ2File('chain_bk','rb')
        return pickle.load(sfile)

   
    def set_proof(self, block, test_proof):
        block['proof'] = test_proof
        return block
    
    def get_previous_block(self):
        # Return last block in the chain
        return self.chain[-1]

    def proof_of_work(self):
        new_proof = 1
        check_proof = False

        if len(self.chain)== 0: # genesis block
            previous_hash = '0' 
            new_block = self.prepare_block(proof = 1, previous_hash = previous_hash)
        else: # usual block
            previous_hash = self.hash(self.chain[-1])
            new_block = self.prepare_block(new_proof,previous_hash)

        while check_proof is False:
            hash_operation = self.hash(new_block)
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
                new_block = self.set_proof(new_block,new_proof)
        
        return new_proof, new_block

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    #Getting the hash of single blocks
    def get_chain(self):
        new_chain = self.load_chain()
        for index,block in enumerate(new_chain):
            hash_block = self.hash(block)
            new_chain[index].update({'hash': hash_block})     

        return new_chain

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index    = 1

        while block_index < len(chain):
            block = chain[block_index]

            if block['previous_hash'] != self.hash(previous_block):
                return False
            
            hash_operation = self.hash(block)
            
            if hash_operation[:4] != '0000':
                return False

            previous_block = block
            block_index += 1
    
        return True

# Mining the Chain

# Initialize WebApp
app = Flask(__name__)

# Creating Blockchain
blockchain = Blockchain()

# Mining new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    proof, new_block = blockchain.proof_of_work()
    mined_block = blockchain.add_block(new_block)

    response = {'message': 'Congratulations, you just mined a block!',
                'index': mined_block['index'],
                'timestamp': mined_block['timestamp'],
                'proof': mined_block['proof'],
                'previous_hash': mined_block['previous_hash'],
                'hash': blockchain.hash(mined_block)}
    
    return jsonify(response), 200

# Getting the full Blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.get_chain(),
                'depth': len(blockchain.chain)}
    return jsonify(response), 200

# Check if the Blockchain is valid
@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    
    if is_valid:
        response = {'message': 'The Blockchain is valid.'}
    else:
        response = {'message': 'The Blockchain is not valid.'}

    return jsonify(response), 200

# Running the App
app.run(host='0.0.0.0',port=5000)