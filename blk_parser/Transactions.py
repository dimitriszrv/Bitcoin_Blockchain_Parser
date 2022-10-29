import hashlib
from hashlib import sha256

from Utility import Utility
from Input_Transactions import Input_Transactions
from Output_Transactions import Output_Transactions

class Transactions:
    # input transactions
    global tx_in
    tx_in = {}
    # output transactions 
    global tx_out
    tx_out = {}
    # data 
    global tx_data
    tx_data = {}

    def __init__(self,_block_file, _tx_in_csv, _tx_out_csv, _timestamp_info_csv, _timestamp):
        self.block_file = _block_file
        self.tx_in_csv = _tx_in_csv
        self.tx_out_csv = _tx_out_csv
        self.timestamp_info_csv = _timestamp_info_csv
        self.timestamp = _timestamp
        self.read_txs()


    def read_txs(self):
        global tx_in, tx_out, tx_data

        # check if segregated witness 
        is_witness = False

        # creation of hash tx id needs whole tx message
        tx_message_start = self.block_file.tell()
        
        # 4 bytes for version of user transaction
        version_of_user_tx = Utility.uint_4_bytes(self.block_file)

        # if is witness must not include marker and flag in calculation of tx id
        # w_start to include version in calculation of tx id if is witness item
        witn_start = self.block_file.tell()
        
        # 1-9 bytes for input transactions
        input_txs_or_witness_marker = Utility.var_int(self.block_file)
        
        # [nVersion][marker][flag][txins][txouts][witness][nLockTime]
        # Witness data is NOT script
        # <https://en.bitcoin.it/wiki/BIP_0141#Transaction_ID>
        
        # check if input_txs_or_witness_marker = 0, then is segregated witness
        if input_txs_or_witness_marker == 0:
            
            # is witness
            is_witness = True      
            pointer_1, pointer_2, witn_end = self.witness()

        else: 
            # input transactions
            # for each input transaction, specify previous_tx_id and previous_tx_index
            for each_input_tx in range(input_txs_or_witness_marker):
                TX_IN = Input_Transactions(self.block_file)
                prev_tx_id = TX_IN.get_previous_tx_id()
                prev_tx_out_index = TX_IN.get_previous_tx_out_index()
                if "tx_in" not in tx_data.keys(): tx_data["tx_in"] = []
                if input_txs_or_witness_marker == 1 and prev_tx_id == "0x" and prev_tx_out_index == -1:
                    tx_in=({"btc_address":"MINING_REWARD","previous_tx_id": prev_tx_id,"previous_tx_index" : prev_tx_out_index})
                else:
                    tx_in=({"btc_address":"NO_ADDRESS","previous_tx_id": prev_tx_id,"previous_tx_index" : prev_tx_out_index})
                tx_data["tx_in"].append(tx_in)
     
            # 1-9 bytes for output transactions
            output_txs = Utility.var_int(self.block_file)
            
            # for each output transaction, specify btc_address and btc_value
            for each_output_tx in range(output_txs):
                TX_OUT = Output_Transactions(self.block_file)
                btc_value = TX_OUT.get_value()
                btc_address = TX_OUT.get_btc_address()
                if "tx_out" not in tx_data.keys(): tx_data["tx_out"] = []
                tx_out = ({"btc_address":btc_address, "btc_value":btc_value})
                tx_data["tx_out"].append(tx_out)

        # 4 bytes for lock time
        lock_time = Utility.uint_4_bytes(self.block_file)
        
        # creation of hash tx id needs whole tx message
        tx_message_end = self.block_file.tell()
        
        # pointer back to tx message start 
        self.block_file.seek(tx_message_start)
        
        # read all tx data: tx_message_end - tx_message_start
        tx_mes = self.block_file.read(tx_message_end - tx_message_start)

        # if is witness remove unwanted fields as marker and flag
        if is_witness:
            # tx_mes[:(witn_start - tx_message_start)], to get version
            # tx_mes[(pointer_1 - tx_message_start):(pointer_2 - tx_message_start)], to get tx message data
            # tx_mes[(witn_end - tx_message_start):] to get all witness stack data 
            tx_mes = tx_mes[:(witn_start - tx_message_start)] + tx_mes[(pointer_1 - tx_message_start):(pointer_2 - tx_message_start)] + tx_mes[(witn_end - tx_message_start):]
        
        # now we must apply SHA256(SHA256(tx_message)) and reverse byte order
        tx_mes = sha256(tx_mes).digest()
        tx_id = sha256(tx_mes).hexdigest()
        tx_id = Utility.reverse_byte_order(tx_id)
        
        for d in tx_data["tx_in"]:
            # if not mining reward
            if d["btc_address"]=="NO_ADDRESS":
                self.tx_in_csv.write(tx_id+"\t"+d["btc_address"]+"\t"+d["previous_tx_id"]+"\t"+str(d["previous_tx_index"])+"\n")
            
        tx_index = 0
        for d in tx_data["tx_out"]:
            self.tx_out_csv.write(tx_id+"\t"+d["btc_address"]+"\t"+str(d["btc_value"])+"\t"+str(tx_index)+"\n")
            tx_index += 1

        self.timestamp_info_csv.write(tx_id+"\t"+str(self.timestamp)+"\n")

        tx_in = {}
        tx_out ={} 
        tx_data = {}

    
    # is Segregated Witness
    def witness(self):
        global tx_in, tx_out, tx_data
        # The marker MUST be a 1-byte zero value: 0x00
        witness_marker = 0
        
        # The flag MUST be a 1-byte non-zero value. Currently, 0x01 MUST be used.
        witness_flag = ord(self.block_file.read(1))
        
        if witness_flag != 0:
            
            # pointer_1 to get start of tx message, if witness
            pointer_1 = self.block_file.tell()
            
            # 1-9 bytes for input transactions 
            input_txs = Utility.var_int(self.block_file)
            
            # for each input transaction, specify previous_tx_id and previous_tx_index
            for each_input_tx in range(input_txs):
                TX_IN = Input_Transactions(self.block_file)
                prev_tx_id = TX_IN.get_previous_tx_id()
                prev_tx_out_index = TX_IN.get_previous_tx_out_index()
                if "tx_in" not in tx_data.keys(): tx_data["tx_in"] = []
                if input_txs == 1 and prev_tx_id == "0x" and prev_tx_out_index == -1:
                    tx_in=({"btc_address":"MINING_REWARD","previous_tx_id": prev_tx_id,"previous_tx_index" : prev_tx_out_index})
                else:
                    tx_in=({"btc_address":"NO_ADDRESS","previous_tx_id": prev_tx_id,"previous_tx_index" : prev_tx_out_index})
            
                tx_data["tx_in"].append(tx_in)
            
            # 1-9 bytes for output transactions
            output_txs = Utility.var_int(self.block_file)
            
            # for each output transaction, specify btc_address and btc_value
            for each_output_tx in range(output_txs):
                TX_OUT = Output_Transactions(self.block_file)
                btc_value = TX_OUT.get_value()
                btc_address = TX_OUT.get_btc_address()
                if "tx_out" not in tx_data.keys(): tx_data["tx_out"] = []
                tx_out = ({"btc_address":btc_address, "btc_value":btc_value})
                tx_data["tx_out"].append(tx_out)

            # pointer_2 to get end of tx message
            pointer_2 = self.block_file.tell()
            
            # <https://en.bitcoin.it/wiki/Weight_units#Detailed_example>
            # now must check for each input number of stack items 
            for s in range(input_txs):
                stack_items = Utility.var_int(self.block_file)
                for st in range(stack_items):
                    size_of_stack_item = Utility.var_int(self.block_file)
                    witness_item = hexlify(self.block_file.read(size_of_stack_item)[::-1]).decode()
                    
            # witn_end to get the end of witness data
            witn_end = self.block_file.tell()
            
        else:
            # witness flag must be != 0
            print("Witness flag must be non zero----\n")
            exit(-1)

        return pointer_1, pointer_2, witn_end