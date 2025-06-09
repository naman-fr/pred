# blockchain_log.py

import json
import hashlib
import time

class BlockchainLogger:
    def __init__(self, filename):
        self.filename = filename
        # Initialize chain with a genesis block if file is empty
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            self.chain = data
        except (FileNotFoundError, json.JSONDecodeError):
            self.chain = []
            # Create genesis block
            genesis = {"index": 0, "timestamp": time.time(),
                       "data": "GENESIS", "prev_hash": "0"}
            genesis["hash"] = self._hash_block(genesis)
            self.chain.append(genesis)
            self._save_chain()

    def _hash_block(self, block):
        """
        Compute SHA-256 hash of a block's contents (excluding its own hash).
        """
        block_str = json.dumps({k: block[k] for k in block if k != "hash"}, 
                               sort_keys=True).encode()
        return hashlib.sha256(block_str).hexdigest()

    def add_record(self, data):
        """
        Add a new record (prediction) as a block to the chain.
        Args:
            data (dict): Prediction data (must include timestamp, etc.).
        """
        prev = self.chain[-1]
        new_block = {
            "index": prev["index"] + 1,
            "timestamp": data.get("timestamp", time.time()),
            "data": data,
            "prev_hash": prev["hash"]
        }
        new_block["hash"] = self._hash_block(new_block)
        self.chain.append(new_block)
        self._save_chain()

    def _save_chain(self):
        """Save the chain (list of blocks) to the JSON file."""
        with open(self.filename, 'w') as f:
            json.dump(self.chain, f, indent=2)
