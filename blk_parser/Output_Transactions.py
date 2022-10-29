import binascii
from binascii import hexlify

from Utility import Utility

class Output_Transactions:

    def __init__(self,_block_file):
        self.block_file = _block_file
        self.value = 0
        self.pubkey_script_length = 0
        self.pubkey_script = ""
        self.decode_pubkey = ""
        self.btc_address = ""
        self.read_output_txs()
    
    def read_output_txs(self):
        
        # 8 bytes for value
        self.value = Utility.uint_8_bytes(self.block_file) / 100000000.0
        
        # 1-9 bytes for public key script length
        self.pubkey_script_length = Utility.var_int(self.block_file)

        # public key script
        self.pubkey_script = hexlify(self.block_file.read(self.pubkey_script_length)).decode()
            
        # get public key without opcodes
        self.decode_pubkey = ""
        try:
            self.decode_pubkey = Utility.remove_upcodes(self.pubkey_script)
        except:
            self.decode_pubkey = ""
        
        
        # flag for btc_address
        # to check if valid or not 
        flag_btc = 0
        
        # photo from here, after ripemd160(sha256(pk))
        # <https://en.bitcoin.it/w/images/en/9/9b/PubKeyToAddr.png>
        
        # 2 hex characters per byte
        
        #---------------------------------------------------------------
        # OP Return
        # null data     
        if str(self.pubkey_script).startswith("6a"):
            self.btc_address = "NULL_DATA"
            flag_btc = 1
        #---------------------------------------------------------------
        
        
        # Bitcoin public keys (traditionally) are 65 bytes (the first of which is 0x04). 
        # They are typically encoded as 130 hex characters.
        elif len(self.decode_pubkey) == 130:
            # Pay to Public Key
            self.btc_address = Utility.pubkey_to_address(self.decode_pubkey).decode()
            flag_btc = 1
        
        # Bitcoin Hash, RIPEMD160(SHA256(pubkey)) is 20 bytes, so encoded as 40 hex chars
        # Hash is a hexadecimal string of 40 characters
        elif len(self.decode_pubkey) == 40:
            
            #---------------------------------------------------------------
            # Pay to Public Key Hash
            if str(self.pubkey_script).startswith("76a914"):
                # prefix version is x00 for main network 
                self.btc_address = Utility.base_58_check(self.decode_pubkey,b"\x00").decode()
                flag_btc = 1
            #---------------------------------------------------------------
            
            #---------------------------------------------------------------
            # Pay to Script Hash
            elif str(self.pubkey_script).startswith("a914"):
                # prefix version is x05 
                self.btc_address = Utility.base_58_check(self.decode_pubkey,b"\x05").decode()
                flag_btc = 1
            #---------------------------------------------------------------
            
            #---------------------------------------------------------------
            # Pay to Witness Public Key Hash      
            elif str(self.pubkey_script).startswith("0014"):
                self.btc_address = Utility.base_32_encode(self.decode_pubkey)
                flag_btc = 1
            #---------------------------------------------------------------
            
        # For segregated witness data, Pay to Witness Script Hash bytes = 32,
        # so 64 chars
        elif len(self.decode_pubkey) == 64:
            
            #---------------------------------------------------------------
            # Pay to Witness Script Hash 
            if str(self.pubkey_script).startswith("0020"):
                self.btc_address = Utility.base_32_encode(self.decode_pubkey)
                flag_btc = 1
            #---------------------------------------------------------------
        
        #---------------------------------------------------------------    
        if flag_btc == 0:
            #print("decode_pubkey: ",len(self.decode_pubkey), self.decode_pubkey)
            self.btc_address = "INVALID_ADDRESS"
        #---------------------------------------------------------------
            

        # <https://en.bitcoin.it/wiki/BIP_0173>
        # Decoders SHOULD enforce known-length restrictions on witness programs. 
        # For example, BIP141 specifies If the version byte is 0, 
        # but the witness program is neither 20 nor 32 bytes, the script must fail.


    # get value
    def get_value(self):
        return self.value

    # get btc address
    def get_btc_address(self):
        return self.btc_address

