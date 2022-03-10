import datetime
import sys 
import binascii
from binascii import hexlify

from Utility import Utility
from Transactions import Transactions


class Block_Header:

    def __init__(self, _block_file, _tx_in_csv, _tx_out_csv, _timestamp_info_csv):
        self.block_file = _block_file
        self.tx_in_csv = _tx_in_csv
        self.tx_out_csv = _tx_out_csv
        self.timestamp_info_csv = _timestamp_info_csv
        self.read_block()

    
    def read_block(self):

        # 4 bytes for magic number
        # .decode() binary -> string
        magic_number = hexlify(self.block_file.read(4)).decode()
        
        # 4 bytes for block size
        block_size = Utility.uint_4_bytes(self.block_file)
        
        # 4 bytes for version
        version = Utility.uint_4_bytes(self.block_file)
        
        # 32 bytes for previous block hash
        prev_block_hash = hexlify(self.block_file.read(32)).decode()
        
        # 32 bytes for merkle root hash
        merkle_root_hash = hexlify(self.block_file.read(32)).decode() 
        
        # 4 bytes for timestamp
        timestamp = Utility.uint_4_bytes(self.block_file)
        creation_time = datetime.datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y %H:%M')
        
        # 4 bytes for difficulty of bits 
        difficulty_bits = Utility.uint_4_bytes(self.block_file)
        
        # 4 bytes for nonce
        nonce = Utility.uint_4_bytes(self.block_file)
        
        # 1-9 bytes for number of transactions within the block
        txs_within_block = Utility.var_int(self.block_file)
        

        # for each transaction within a block
        for each_tx in range(txs_within_block):
            Transactions(self.block_file, self.tx_in_csv, self.tx_out_csv, self.timestamp_info_csv, timestamp)
