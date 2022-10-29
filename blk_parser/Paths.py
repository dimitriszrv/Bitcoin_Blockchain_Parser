import os
import shutil

class Paths:

    def info():
        print("\n\n\t\t\t#############################################")
        print("\t\t\t# Bitcoin Blockchain blkXXXXX.dat parser    #")
        print("\t\t\t#\t\t\t\t\t    #")
        print("\t\t\t#\tCopyright (C) 2021 Dimitrios Zervas #")
        print("\t\t\t#############################################")
        print("\n\n> This script aimed to parse raw Bitcoin Blockchain Transactions")
        print("> Read 'Hints.txt' before running the script!")
        print("---------------------------------------------------------------------------------------------\n")
    
    def db_info():
        print("\t\t\t\t\t\t\t\t\tDatabase Error Hints")
        print("> Hint 1 \n\n - Make sure host, user & password fields are correct at class Database.py : line 25\n")
        print("> Hint 2\n\n - If DatabaseError: 1290 (HY000):\n \
        The MySQL server is running with the --secure-file-priv option \n\t So it cannot execute this statement\n")
        print("\t> Run    $ sudo gedit[or vi] '/etc/mysql/mysql.conf.d/mysqld.cnf'")
        print('''\t> Add secure_file_priv="" at the end of the file\n''')
        print("> Hint 3\n\n - If ProgrammingError: 3948 (42000):\n \
        Loading local data is disabled; this must be enabled on both the client and server sides\n")
        print('''\t> Connect to mysql and run\t--\t mysql> SET GLOBAL local_infile="ON";''')
        print("---------------------------------------------------------------------------------------------\n")

    def continue_(path):
        # calculate size of all blkXXXXX.dat files
        files_ = sorted([path+x for x in os.listdir(path) if x.startswith("blk") and x.endswith(".dat")])
        calc_size = float(sum([os.path.getsize(x) for x in files_]) / 10**9)
        if calc_size.is_integer():
            c_size = int(calc_size)
            gb = c_size
        else:
            if len(str(calc_size)) > 5: 
                c_size = format(calc_size, ".3f")
            gb = format(calc_size, ".1f")

        print("> All blkXXXXX.dat files are %s GB" % c_size)
        print("> So you must be carefull while running this parser")
        print("> Because it needs (extra) ~ %s GB of storage for preprocessing" %(4*float(gb)))
        print("> Make sure you have enough free space\n")
        print("> If you want to keep blkXXXXX.dat files after parsing \t\t> Press 'y'")
        print("> If you want to delete blkXXXXX.dat files after parsing \t> Press 'n'")
        print("---------------------------------------------------------------------------------------------\n")

        c_choice = (input("> Should the parser delete the files? [y/n]\t> ")).lower()
        while True:
            if c_choice == "y" or c_choice == "n":
                print("---------------------------------------------------------------------------------------------\n")
                break
            else:
                print("\n> Wrong choice, choice must be 'y' or 'n'")
                c_choice = (input("> Should the parser delete blkXXXXX.dat files? [y/n]\t> ")).lower()

        return c_choice


    def get_input_path(fl = ".dat"):
        print("\t\t\t\t\t\t\t\t\tInput directory path")
        inp = input("\n> Please enter the full path where blkXXXXX%s files are stored\n> " %fl)
        if not inp.startswith("/"): inp = "/"+inp
        while True:
            if os.path.exists(inp):
                break
            else:
                #while not os.path.exists(inp):
                print("\n> Input path does not exists...")
                print("> Please enter the full path where blkXXXXX%s files are stored" % fl)
                inp = input("> If you want to quit press 'q'\t> ")
                if inp == "q" or inp == "Q": 
                    print("> Exiting...")
                    print("---------------------------------------------------------------------------------------------\n")
                    exit(-1)
                if not inp.startswith("/"): inp = "/"+inp

        if not inp.endswith("/"): inp += "/"
        count_f = len([x for x in os.listdir(inp) if x.startswith("blk") and x.endswith(fl)])
        print("> Valid input path -- %s\t> Number of files: %d" % (inp,count_f))
        print("---------------------------------------------------------------------------------------------\n")
        return inp, count_f
        
    
    def get_export_path(inp):
        print("\t\t\t\t\t\t\t\t\tExport directory path")
        print("> Path must be different than Input directory path...")
        exp = input("> Please enter the full path where Bitcoin transaction files will be stored\n> ")
        if not exp.startswith("/"): exp = "/"+exp
        if not exp.endswith("/"): exp = exp+"/"
        
        while True:
            if os.path.exists(exp):
                if exp == inp:
                    print("\n> Path must be different than Input directory path...")
                    exp = input("> Please enter the full path where Bitcoin transaction files will be stored\n> ")
                    if not exp.startswith("/"): exp = "/"+exp
                    if not exp.endswith("/"): exp = exp+"/"
                else:
                    break
            else:
                print("\n> Export path is not valid, please enter a valid path...")
                exp = input("> If you want to quit press 'q'\t> ")
                if exp == "q" or exp == "Q": 
                    print("> Exiting...")
                    print("---------------------------------------------------------------------------------------------\n")
                    exit(-1)
                if not exp.startswith("/"): exp = "/"+exp
        if not exp.endswith("/"): exp += "/"
        print("> Valid export path -- %s" % exp)
        print("---------------------------------------------------------------------------------------------\n")
        return exp


    def create_dirs(c_dir):
        # create a folder for all transaction inputs
        transaction_inputs = c_dir+"Transaction_inputs/"
        if os.path.exists(transaction_inputs): shutil.rmtree(transaction_inputs)
        os.mkdir(transaction_inputs)

        # create a folder for all transaction outputs
        transactions_outputs = c_dir+"Transaction_outputs/"
        if os.path.exists(transactions_outputs): shutil.rmtree(transactions_outputs)
        os.mkdir(transactions_outputs)
        
        # create a folder for timestamp info
        timestamp_info = c_dir+"Timestamp_info/"
        if os.path.exists(timestamp_info): shutil.rmtree(timestamp_info)
        os.mkdir(timestamp_info)

        return transaction_inputs, transactions_outputs, timestamp_info#, transactions_path


    def create_files(in_, out_, time_, file_):
        # create csv file with transaction inputs
        tx_in_csv = open(in_+"in"+file_[3:-3]+"csv","w")
        tx_in_csv.write("tx_id\tbtc_address\tprevious_tx_id\tprevious_tx_index\n")
                
        # create csv file with transaction outputs
        tx_out_csv = open(out_+"out"+file_[3:-3]+"csv","w")
        tx_out_csv.write("tx_id\tbtc_address\tbtc_value\ttx_index\n")    

        # create csv file with timestamp information
        time_info = open(time_+"info"+file_[3:-3]+"csv","w")
        time_info.write("tx_id\ttimestamp\n")

        return tx_in_csv, tx_out_csv, time_info


    def goodbye(c_dir):
        d_ = c_dir+"bitcoin_info.json"
        print("> Bitcoin transactions are in: '%s'" %d_)
        print("> Don't forget to change file permissions, execute: \n\t$ sudo chmod 777 %s\n"%d_)
        print("> Exiting...")
        print("---------------------------------------------------------------------------------------------\n")

    

        