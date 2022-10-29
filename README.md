# Bitcoin_Blockchain_Parser 
This script aims to parse raw Bitcoin Blockchain transactions.</br>
<a href="https://github.com/dimitriszrv/Bitcoin_Blockchain_Parser/blob/main/Thesis_Dimitrios_Zervas.pdf">Master's Thesis</a> on Dept. of <a href="https://www.cs.uoi.gr/?lang=en">Computer Science & Engineering</a>, University of Ioannina, Greece.

## About
As data is encoded and stored on <a href="https://bitcoin.org/en/download"> Bitcoin Core </a> in binary format, decoding is done to specify fields for handling transactions between users. Those fiels are:</br> 
- `Inputs` that specify the address of sender and value that was sent.</br>
- `Outputs` that specify the corresponding address of recipient and value that was received.</br>
- `Timestamp` that specifies the time when transaction took place.</br></br>

However, inputs don't contain info about the sender address but a pointer to a previous transaction (UTXO) that took place when (current) sender was the receiver. 
For example, 
```
> in transaction with tx_id_1: a16f3ce4dd5deb92d98ef5cf8afeaf0775ebca408f708b2146c4fb42b41e14be
~ inputs is:  {btc_address: NO_ADDRESS,
               previous_tx_id: f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16,
               previous_tx_index: 1}},
             
> in transaction with tx_id_2: f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16
~ outputs: [{btc_value: 10.0, btc_address: 1Q2TWHE3GMdB6BZKafqwxXtWAWgFt5Jvm3},
            {btc_value: 40.0, btc_address: 12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S}]}
-----------------------------------------------------------------------------------------------
Consequently, the input address of tx_id_1 is given by the output address of the previous_tx_id 
and previous_tx_index (tx_id_2).
So the input address of tx_id_1 is: 12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S.            
```

The process of readdressing is done using MySQL in order to find the missing sender addresses.</br>

## Getting started 
#### Prerequisites
- Install the required libraries using Python3, run:</br>
```bash
$ pip3 install -r requirements.txt
```
- As address preprocessing is done with MySQL, before running the script, do steps from 2 to 5 on <a href="https://github.com/dimitriszrv/Bitcoin_Blockchain_Parser/blob/main/Hints.txt">Hints.txt</a>.</br>

## Decoding the data 

**Fire up terminal, and let's go!** :zap:  :computer: </br>
```bash
$ python3 Main.py
```
---

- You will be asked where blk files at, make sure to give the full input path.</br>
- Also you will be asked if you want to keep or delete blk_files, answer must be y/n.</br>
<img align="center" src="https://user-images.githubusercontent.com/17187213/157711065-eba65550-b8df-4cdf-bc58-9732484dc119.png"></br></br>
- Give the full export path where data will be saved.</br>
<img align="center" src="https://user-images.githubusercontent.com/17187213/157712194-8b9ce74f-03a8-4382-aad8-890ffcabb488.png"></br></br>
- Connecting to database, loading data and start readdressing.</br>
<img align="center" src="https://user-images.githubusercontent.com/17187213/157712201-71894d29-dca2-4761-8028-44c07aaadd1d.png">
<img align="center" src="https://user-images.githubusercontent.com/17187213/157712210-1bbc1593-2009-4422-9b42-ae824785ac81.png">
<img align="center" src="https://user-images.githubusercontent.com/17187213/157712227-b91e7e8a-e6aa-46bf-8dd3-9ef9d2d3e274.png">
<img align="center" src="https://user-images.githubusercontent.com/17187213/157712238-7205ef38-bc11-4a5c-bc2c-33e184e1c8e0.png"></br>

- After parsing data, because MySQL has some restrictions and limitations, full permissions must be given to json file created with (ex):
```bash 
$ sudo chmod 777 ~/full_path/Bitcoin_Transactions/bitcoin_info.json
```

## Dataset
Dataset is saved at selected export path at **bitcoin_info.json** file.


```json
{{"tx_id": "f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16", "inputs": ["12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S"], "outputs": [{"btc_value": 10.0, "btc_address": "1Q2TWHE3GMdB6BZKafqwxXtWAWgFt5Jvm3"}, {"btc_value": 40.0, "btc_address": "12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S"}], "timestamp": 1231731025},
{"tx_id": "a16f3ce4dd5deb92d98ef5cf8afeaf0775ebca408f708b2146c4fb42b41e14be", "inputs": ["12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S"], "outputs": [{"btc_value": 30.0, "btc_address": "12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S"}, {"btc_value": 10.0, "btc_address": "1DUDsfc23Dv9sPMEk5RsrtfzCw5ofi5sVW"}], "timestamp": 1231740133},
{"tx_id": "591e91f809d716912ca1d4a9295e70c3e78bab077683f79350f101da64588073", "inputs": ["12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S"], "outputs": [{"btc_value": 29.0, "btc_address": "12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S"}, {"btc_value": 1.0, "btc_address": "1LzBzVqEeuQyjD2mRWHes3dgWrT9titxvq"}], "timestamp": 1231740736},
{"tx_id": "12b5633bad1f9c167d523ad1aa1947b2732a865bf5414eab2f9e5ae5d5c191ba", "inputs": ["12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S"], "outputs": [{"btc_value": 1.0, "btc_address": "13HtsYzne8xVPdGDnmJX8gHgBZerAfJGEf"}, {"btc_value": 28.0, "btc_address": "12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S"}], "timestamp": 1231742062},
{"tx_id": "4385fcf8b14497d0659adccfe06ae7e38e0b5dc95ff8a13d7c62035994a0cd79", "inputs": ["13HtsYzne8xVPdGDnmJX8gHgBZerAfJGEf"], "outputs": [{"btc_value": 1.0, "btc_address": "15NUwyBYrZcnUgTagsm1A7M2yL2GntpuaZ"}], "timestamp": 1231744600}, {"..."}}
```

## License
This project is licensed under the terms of the <a href="https://github.com/dimitriszrv/Bitcoin_Blockchain_Parser/blob/main/LICENSE"> GNU GPL v3.0</a>.

- #### Find me: zervasdm@gmail.com

- #### Donate (BTC): bc1q9gr9xe802zujwwrhswgty4awz8wellkkkal3w7

