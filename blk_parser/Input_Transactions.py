import binascii
from binascii import hexlify

from Utility import Utility


class Input_Transactions:

    def __init__(self,_block_file):
            self.block_file = _block_file
            self.previous_tx_id = ""
            self.previous_tx_out_index = 0
            self.script_length = 0
            self.signature_script = ""
            self.sequence_number = ""
            self.read_input_txs()

    def read_input_txs(self):    
        # if prev_tx_id = 0x0000000000000000000000000000000000000000000000000000000000000000,
        # previous_tx_out_index = -1, 
        # and input_count = 1, then check for coinbase tx
        
        # 32 bytes for previous transaction id
        self.previous_tx_id = Utility.reverse_byte_order(hexlify(self.block_file.read(32)).decode())

        if self.previous_tx_id == "0000000000000000000000000000000000000000000000000000000000000000": # "0"*64
            self.previous_tx_id = "0x"

        # 4 bytes for previous transaction out index
        self.previous_tx_out_index = Utility.uint_4_bytes(self.block_file)
        
        # if index 0xffffffff, then coinbase tx
        if self.previous_tx_out_index == 4294967295:
            self.previous_tx_out_index = -1 
        
        # 1-9 bytes for script length
        self.script_length = Utility.var_int(self.block_file)
        
        # signature script
        self.signature_script = hexlify(self.block_file.read(self.script_length)).decode()

        # 4 bytes for sequence number
        self.sequence_number = Utility.uint_4_bytes(self.block_file)


    # get previous tx id
    def get_previous_tx_id(self):
        return self.previous_tx_id

    # get previous tx out index
    def get_previous_tx_out_index(self):
        return self.previous_tx_out_index

    # get script length
    def get_script_length(self):
        return self.script_length

    # get signature script
    def get_signature_script(self):
        return self.signature_script

    # get sequence number
    def get_sequence_number(self):
        return self.sequence_number
