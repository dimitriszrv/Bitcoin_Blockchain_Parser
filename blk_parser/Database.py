import mysql.connector as conn
import csv
import shutil
import os
import alive_progress
from alive_progress import alive_bar

class Database:

    def __init__(self, _c_dir):
 
        # paths
        self.c_dir = _c_dir
        self.tx_inputs_path = self.c_dir + "Transaction_inputs/"
        self.tx_outputs_path = self.c_dir + "Transaction_outputs/"
        self.timestamp_info_path = self.c_dir + "Timestamp_info/"

        # change fields below
        self.host = "localhost"         # change host
        self.user = "root"              # change user
        self.password = "sql123456"     # change password


    def create_tables(self):
        try:
            # connect to database
            db = conn.connect(host = self.host, user = self.user, password = self.password, allow_local_infile=True)
            cursor = db.cursor()
            if conn:
                print("---------------------------------------------------------------------------------------------\n")
                print("> Connection to Database Established...")

                # create database
                cursor.execute("DROP DATABASE IF EXISTS Bitcoin_Transactions")
                cursor.execute("CREATE DATABASE Bitcoin_Transactions")
                print("> Database 'Bitcoin_Transactions' created successfully...")
                cursor.execute("USE Bitcoin_Transactions")

                # creating table transaction_inputs
                print("> Creating table: transaction_inputs")
                cursor.execute("DROP TABLE IF EXISTS transaction_inputs")
                cursor.execute("""CREATE TABLE transaction_inputs (
                    tx_id VARCHAR(255) NOT NULL,
                    btc_address VARCHAR(255) NOT NULL,
                    previous_tx_id VARCHAR(255) NOT NULL,
                    previous_tx_index INT NOT NULL)
                    ENGINE=InnoDB""")

                # creating table transaction_outputs
                print("> Creating table: transaction_outputs")
                cursor.execute("DROP TABLE IF EXISTS transaction_outputs")
                cursor.execute("""CREATE TABLE transaction_outputs (
                    tx_id VARCHAR(255) NOT NULL,
                    btc_address VARCHAR(255) NOT NULL,
                    btc_value DOUBLE NOT NULL,
                    tx_index INT NOT NULL)
                    ENGINE=InnoDB""")

                # creating table timestamp_info
                print("> Creating table: timestamp_info")
                cursor.execute("DROP TABLE IF EXISTS timestamp_info")
                cursor.execute("""CREATE TABLE timestamp_info (
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    tx_id VARCHAR(255) NOT NULL,
                    timestamp INT NOT NULL)
                    ENGINE=InnoDB""")
                db.commit()
                print()

                return db, cursor

        except conn.Error as e:
            print ("Connection to Database Not Established...\n",e)
            exit(-1)


    def load_into_tables(self, db, cursor):
        cursor.execute('''SET GLOBAL local_infile="ON";''')
        cursor.execute("SET SESSION group_concat_max_len=15000000;")
        cursor.execute("SET GLOBAL sort_buffer_size = 256000000;")
        db.commit()
        # transaction inputs
        print("> Loading Transaction_inputs into\t- Database:\tBitcoin_Transactions\n\t\t\t\t\t- Table:\ttransaction_inputs\n")
        Database.load_files(self.tx_inputs_path, db, cursor, "in", "transaction_inputs")

        # transaction outputs
        print("> Loading Transaction_outputs into\t- Database:\tBitcoin_Transactions\n\t\t\t\t\t- Table:\ttransaction_outputs\n")
        Database.load_files(self.tx_outputs_path, db, cursor, "out", "transaction_outputs")

        # timestamp info
        print("> Loading Timestamp_info into\t\t- Database:\tBitcoin_Transactions\n\t\t\t\t\t- Table:\ttimestamp_info\n")
        Database.load_files(self.timestamp_info_path, db, cursor, "info", "timestamp_info")


    def load_files(path, db, cursor, ch, table):
        # ch is "in", "out" or "info"
        csv_files = sorted([x for x in os.listdir(path) if x.startswith(ch) and x.endswith(".csv")])

        with alive_bar(len(csv_files), bar = "smooth") as bar:
            for c in csv_files:
                print(c)
                if ch == "info":
                    cursor.execute("""
                        LOAD DATA LOCAL INFILE '%s'
                        INTO TABLE %s COLUMNS TERMINATED BY '\t' LINES TERMINATED BY '\n' IGNORE 1 LINES (tx_id, timestamp);
                    """%(path+c,table))
                    db.commit()
                else:
                    cursor.execute("""
                        LOAD DATA LOCAL INFILE '%s'
                        INTO TABLE %s COLUMNS TERMINATED BY '\t' LINES TERMINATED BY '\n' IGNORE 1 LINES;
                    """%(path+c,table))
                    db.commit()

                # delete current file after parsing to database
                os.remove(path+c)

                bar()
        print("\n> Done...\n---------------------------------------------------------------------------------------------\n")
        # deleting folder
        shutil.rmtree(path)


    def readdress(self, db, cursor):
        # readdress those addresses that are NO_ADDRESSES
        print("> Readdressing\n> This may take a while, please wait...")
        # creating a new table readdress, with all matched addresses that are NO_ADDRESS
        cursor.execute("""
            CREATE TABLE readdress
            SELECT transaction_inputs.tx_id, transaction_outputs.btc_address
            FROM transaction_inputs
            INNER JOIN transaction_outputs
            ON transaction_outputs.tx_id = transaction_inputs.previous_tx_id
            AND transaction_outputs.tx_index = transaction_inputs.previous_tx_index;
        """)
        db.commit()
        cursor.execute("DROP TABLE transaction_inputs;")
        db.commit()
        print("> Creating a new table with updated transaction inputs info")
        # now grouping by all btc_addresses from same tx_id
        cursor.execute("SET SESSION group_concat_max_len=15000000;")
        cursor.execute("SET GLOBAL sort_buffer_size = 256000000;")
        db.commit()
        cursor.execute("""
            CREATE TABLE upd_transaction_inputs
            SELECT tx_id, JSON_ARRAYAGG(btc_address) AS inputs
            FROM readdress
            GROUP BY tx_id;
        """)
        db.commit()


        cursor.execute("DROP TABLE readdress;")
        db.commit()

        print("> Creating a new table with updated transaction outputs info")
        # update transaction outputs table, group by all btc_addresses from same tx_id
        cursor.execute("""
            CREATE TABLE upd_transaction_outputs
            SELECT tx_id, JSON_ARRAYAGG(JSON_OBJECT("btc_address", btc_address, "btc_value", btc_value)) AS outputs
            FROM transaction_outputs
            GROUP BY tx_id;
        """)
        cursor.execute("DROP TABLE transaction_outputs;")
        db.commit()


        # join tables on tx_id
        cursor.execute("SET GLOBAL sort_buffer_size = 256000000;")
        db.commit()
        print("> Matching and cleaning up the data")
        cursor.execute("""
            CREATE TABLE bitcoin_info
            SELECT timestamp_info.tx_id, timestamp_info.timestamp, upd_transaction_inputs.inputs, upd_transaction_outputs.outputs
            FROM timestamp_info
            INNER JOIN upd_transaction_inputs ON upd_transaction_inputs.tx_id = timestamp_info.tx_id
            INNER JOIN upd_transaction_outputs ON upd_transaction_outputs.tx_id = timestamp_info.tx_id ORDER BY id;
        """)
        db.commit()


        # export to json file
        print("> Saving data into folder '%s'"%self.c_dir)
        d_ = self.c_dir+"bitcoin_info.json"
        cursor.execute("""
            SELECT JSON_OBJECT("tx_id",tx_id,"timestamp",timestamp,"inputs",inputs,"outputs",outputs)
            FROM bitcoin_info
            INTO OUTFILE '%s';
        """%d_)
        db.commit()

        cursor.execute("DROP DATABASE Bitcoin_Transactions;")
        db.commit()
        # drop tables and database
        print("\n> Done...\n---------------------------------------------------------------------------------------------\n")


