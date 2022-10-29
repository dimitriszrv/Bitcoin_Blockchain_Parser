import struct
import binascii
import hashlib
import base58
from hashlib import sha256
from binascii import hexlify, unhexlify


class Utility:


    # read unsigned integers from block chain

    # H = unsigned short
    # Q = unsigned long long
    # I = unsigned int
    # struct until 8 bytes 

    #def uint_1_byte(var):
    #    return int.from_bytes(var.read(2), byteorder="little")

    # unsigned for 2 bytes, unsigned short int
    def uint_2_bytes(var):
        #return int.from_bytes(var.read(2), byteorder="little")
        return struct.unpack("H", var.read(2))[0]

    # unsigned for 4 bytes, unsigned int
    def uint_4_bytes(var):
        #return int.from_bytes(var.read(4), byteorder="little")
        return struct.unpack("I", var.read(4))[0]

    # unsigned for 8 bytes, unsigned long long int
    def uint_8_bytes(var):
        #return int.from_bytes(var.read(8), byteorder="little")
        return struct.unpack("Q", var.read(8))[0]


    # variable integer to indicate number of upcoming fields
    def var_int(blk_file):

        # number of upcoming fields
        n_upcoming_fields = ord(blk_file.read(1))
        
        # there is no prefix of fd, fe, or ff, so we know this 1 byte is the var_int value, 
        # and we can convert hexadecimal straight to decimal:
        # ----------------------------------------
        # value: >=0 and <=252, bytes_used: 1, format: uint8_t
        if n_upcoming_fields < 0xfd: 
            return n_upcoming_fields #int.from_bytes(n_upcoming_fields, byteorder="little")
        
        
        # the prefix is fd, so we know the next 2 bytes (in little-endian) 
        # is going to give us the size of the upcoming field:
        # ----------------------------------------
        # value: >=253 and <=0xffff, bytes_used: 2, format: 0xfd followed by the number as uint16_t
        if n_upcoming_fields == 0xfd: # 0xfd = 253
            return Utility.uint_2_bytes(blk_file)
        
        
        # the predix fe means it’s the next 4 bytes
        # ----------------------------------------
        # value: >=0x10000  and <=0xffffffff, bytes_used: 5, format: 0xfe followed by the number as uint32_t
        elif n_upcoming_fields == 0xfe:  #0xfe = 254
            return Utility.uint_4_bytes(blk_file)
        
        
        # the predix ff means it’s the next 4 bytes
        # ----------------------------------------
        # value: >=0x100000000  and <=0xffffffffffffffff, bytes_used: 9, format: 0xff followed by the number as uint64_t
        elif n_upcoming_fields == 0xff: #0xff = 255
            return Utility.uint_8_bytes(blk_file)

    #---------------------------------------------------------------------------------------------------------------
    # <https://en.wikipedia.org/wiki/Endianness
    def reverse_byte_order(endian):
        return ''.join(reversed([endian[i:i+2] for i in range(0, len(endian), 2)]))
    #---------------------------------------------------------------------------------------------------------------

    #---------------------------------------------------------------------------------------------------------------
    # <https://en.bitcoin.it/wiki/Script#Constants>
    # remove opcodes if exist
    def remove_upcodes(script):

        data = ''
        # index i, iterate chars 2 by 2
        i = 0 
        
        while i < len(script) - 1:
            
            char_1 = script[i] # ex a = '4'
            char_2 = script[i+1] # ex b = '1'
            
            # check if opcode is in range 01 - 4b, get the data
            
            # <https://wiki.bitcoinsv.io/index.php/Pushdata_Opcodes>
            # Opcodes 1-75 (0x01 - 0x4b), 
            # simply push their value of bytes of data onto the stack.
            
            opcode = int(char_1+char_2,16)
            
            if opcode>=1 and opcode<=75:
                i+=2
                # get the bytes needed 
                bytes_to_push_into_stack = opcode
                # index j, while loop to get specific length of data
                j = 0
                while j < bytes_to_push_into_stack * 2:
                    try:
                        data += script[i+j]
                    except IndexError:
                        return data
                    j += 1
                # reset index i, for char_1 and char_2
                i += j - 2   
            # next 2 chars
            i+=2

        return data
    #---------------------------------------------------------------------------------------------------------------


    #---------------------------------------------------------------------------------------------------------------
    #<https://en.bitcoin.it/wiki/Technical_background_of_version_1_Bitcoin_addresses>
    def pubkey_to_address(p_key):
        # digest(), to return the ascii encoding style result: \x..\x..\x..
        # hexdigest .. .. ..
        
        # Unicode-objects must be encoded before hashing
        obj_key = binascii.unhexlify(p_key)
        
        # Step 2: Perform SHA-256 hashing on the public key
        step_2 = sha256(obj_key).digest()
        
        # Step 3: Perform RIPEMD-160 hashing on the result of SHA-256
        step_3 = hashlib.new("ripemd160", step_2).digest()

        # ex step_3 -> b"b\xe9\x07\xb1\\\xbf'\xd5BS\x99\xeb\xf6\xf0\xfbP\xeb\xb8\x8f\x18" 
        # step_3.hex() -> 62e907b15cbf27d5425399ebf6f0fb50ebb88f18
        
        # version = (0x00 for Main Network)
        return Utility.base_58_check(binascii.hexlify(step_3),b"\x00")
    #---------------------------------------------------------------------------------------------------------------

    #<https://en.bitcoin.it/wiki/Technical_background_of_version_1_Bitcoin_addresses>
    #<https://en.bitcoin.it/wiki/Base58Check_encoding>
    def base_58_check(ripemd_160_hash,version):
        
        #Unicode-objects must be encoded before hashing
        obj_hash = binascii.unhexlify(ripemd_160_hash)
        
        # Step 4: Add version byte in front of RIPEMD-160 hash (0x00 for Main Network)
        # version = 0x05 for P2SH
        step_4 =  version + obj_hash
        
        # Step 5: Perform SHA-256 hash on the extended RIPEMD-160 result
        step_5 = sha256(step_4).digest()
        
        # Step 6: Perform SHA-256 hash on the result of the previous SHA-256 hash
        step_6 = sha256(step_5).digest()
        
        # Step 7: Take the first 4 bytes of the second SHA-256 hash. 
        # This is the address checksum
        checksum = step_6[:4]
        
        # Step 8: Add the 4 checksum bytes from stage 7 at the end of extended RIPEMD-160 hash from stage 4. 
        # This is the 25-byte binary Bitcoin Address.
        step_4 += checksum
        
        # Step 9: Convert the result from a byte string into a base58 string using Base58Check encoding. 
        # This is the most commonly used Bitcoin Address format
        
        final_address = base58.b58encode(step_4)
        return final_address

    #<https://en.bitcoin.it/wiki/Bech32>
    def base_32_encode(val):

        # val is 00207bc3b9fcc5eab619a686361476e39f33b94bd8b70a9a9d45c81fe49dd30f3f9c
        # after removing opcodes -> 7bc3b9fcc5eab619a686361476e39f33b94bd8b70a9a9d45c81fe49dd30f3f9c
        # we convert to binary and the result is 4-bit unsigned integers
        # and Bech32 encoding converts this to a 5-bit unsigned integers 
        # so we divide the 4 binary digits into 5 bit sections
        dec_data, bech_32 = Utility.divide_to_5_bits(val)

        # compute the checksum by using the data, where data is decimal representation
        # and the human readable portion (HRP) - (bc for MainNet and tb for TestNet)
        # ex [10, 8, 22, 6, 12, 0] 
        bech_32_checksum = Utility.bech32_create_checksum("bc",dec_data)
        
        # map to bec 32 chars, 10 -> '2', 8 -> 'g' ...
        # ex ['2', 'g', 'k', 'x', 'v', 'q']    
        bech_32_checksum = [Utility.map_to_bec32_chars(str(i)) for i in bech_32_checksum]
        
        # ex 2gkxvq
        bech_32_checksum = "".join(x for x in bech_32_checksum)
        
        # after mapping all chars, Bech32 address = hrp + separator + data + checksum
        # hrp = "bc" (mainnet), separator = 1
        bech_32_address = "bc1" + bech_32 + bech_32_checksum

        return bech_32_address

    #<https://en.bitcoin.it/wiki/Bech32>
    # Step 4: Divide the 4 binary digits into 5 bit sections

    def divide_to_5_bits(s_string):
        
        bech_32_chars = ""
        get_data = ""
        decimal_data = []
        
        for s in s_string:
            # [2:0] to remove 0b111 and zfill for prefix
            get_data += str(bin(int(s, 16))[2:].zfill(4))
        
        # add the witness version byte in front of the step 4 result (current version is 0x00)
        get_data = "00000" + get_data
        
        # change the spacing of the 1's and zeros 
        # so that they are grouped 5! in a set instead of 4:
        while True:
                    
            # binary to decimal
            each_decimal = int(get_data[:5],2)
            decimal_data.append(each_decimal)
            get_data = get_data[5:]
            
            
            # map each 5 bits to bec 32 char
            bech_32_chars += Utility.map_to_bec32_chars(str(each_decimal))
            
            if len(get_data) == 0:
                break

        return decimal_data, bech_32_chars
    
    # now we map each 5 bits into the table here
    #<https://en.bitcoin.it/wiki/BIP_0173#Bech32>

    def map_to_bec32_chars(bits_5):
        if bits_5 == "0": return "q"
        elif bits_5 == "1": return "p"
        elif bits_5 == "2": return "z"
        elif bits_5 == "3": return "r"
        elif bits_5 == "4": return "y"
        elif bits_5 == "5": return "9"
        elif bits_5 == "6": return "x"
        elif bits_5 == "7": return "8"
        elif bits_5 == "8": return "g"
        elif bits_5 == "9": return "f"
        elif bits_5 == "10": return "2"
        elif bits_5 == "11": return "t"
        elif bits_5 == "12": return "v"
        elif bits_5 == "13": return "d"
        elif bits_5 == "14": return "w"
        elif bits_5 == "15": return "0"
        elif bits_5 == "16": return "s"
        elif bits_5 == "17": return "3"
        elif bits_5 == "18": return "j"
        elif bits_5 == "19": return "n"
        elif bits_5 == "20": return "5"
        elif bits_5 == "21": return "4" 
        elif bits_5 == "22": return "k"  
        elif bits_5 == "23": return "h"
        elif bits_5 == "24": return "c"
        elif bits_5 == "25": return "e"
        elif bits_5 == "26": return "6"
        elif bits_5 == "27": return "m"
        elif bits_5 == "28": return "u"
        elif bits_5 == "29": return "a"
        elif bits_5 == "30": return "7"
        elif bits_5 == "31": return "l"
        
    def bech32_polymod(values):
        GEN = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
        chk = 1
        for v in values:
            b = (chk >> 25)
            chk = (chk & 0x1ffffff) << 5 ^ v
            for i in range(5):
                chk ^= GEN[i] if ((b >> i) & 1) else 0
        return chk

    def bech32_hrp_expand(s):
        return [ord(x) >> 5 for x in s] + [0] + [ord(x) & 31 for x in s]

    def bech32_verify_checksum(hrp, data):
        return Utility.bech32_polymod(Utility.bech32_hrp_expand(hrp) + data) == 1

    def bech32_create_checksum(hrp, data):
        values = Utility.bech32_hrp_expand(hrp) + data
        polymod = Utility.bech32_polymod(values + [0,0,0,0,0,0]) ^ 1
        return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]
        
            