import os
import shutil
import csv
import alive_progress
from alive_progress import alive_bar

from Block_Header import Block_Header
from Paths import Paths
from Database import Database

# for linux
# import os
# desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')

# for windows
# desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 


class Main:

    # script informations
    Paths.info()

    # database informations
    # Paths.db_info()

    all_files = 0 

    while all_files == 0:
        # get the input path where blkXXXXX.dat files are stored 
        # and check if there are blkXXXXX.dat files
        input_path, all_files = Paths.get_input_path()

        if all_files == 0:
            print("> There are no blkXXXXX.dat files there...")

    del_choice = Paths.continue_(input_path)

    # get the path where blkXXXXX files will be stored
    c_dir = Paths.get_export_path(input_path)
    for d in os.listdir(c_dir): os.remove(c_dir+d)

   
    # create 4 folders, one to keep all transaction inputs, one for all transaction outputs and one for timestamp info
    #------------------------------------------------------------------------------
    # > tx_inputs_path folder for transaction inputs     --      has csv files with columns  
    # tx_id     btc_address     previous_tx_id      previous_tx_index
    #------------------------------------------------------------------------------
    # > tx_outputs_path folder for transaction outputs    --      has csv files with columns 
    # tx_id     btc_address     btc_value       tx_index        
    #------------------------------------------------------------------------------
    # > timestamp_info_path folder for timestamp info     --      has csv files with columns  
    # tx_id     timestamp
    #------------------------------------------------------------------------------
    # > transactions_path folder for bitcoin blockchain transactions final data
    # tx_id     sender      receiver      btc_value       timestamp
    
    tx_inputs_path, tx_outputs_path, timestamp_info_path = Paths.create_dirs(c_dir)

    print()

    with alive_bar(all_files, bar = "smooth") as bar:

        for f in sorted(os.listdir(input_path)):

            if f.startswith("blk") and f.endswith(".dat"):

                # each_dat is full path of file, ex /../blk00000.dat
                each_dat = os.path.join(input_path,f)
                    
                # f = blk00000.dat
                print(f)

                # create files 
                # tx_in_csv stored into transaction_inputs folder 
                # tx_out_csv stored into transaction_outputs folder
                # timestamp_info_csv stored into timestamp_info folder

                # ex for blk00000.dat, 
                # tx_in_csv             ->      in00000.csv
                # tx_out_csv            ->      out00000.csv
                # timestamp_info_csv    ->      info00000.csv
                tx_in_csv, tx_out_csv, timestamp_info_csv = Paths.create_files(tx_inputs_path, tx_outputs_path, timestamp_info_path, f)

                with open(each_dat,"rb") as block_file:
                    while True:     
                        # if end of file
                        if block_file.tell() == os.fstat(block_file.fileno()).st_size:
                            tx_in_csv.close()
                            tx_out_csv.close()
                            timestamp_info_csv.close()
                            # keep of delete parsed blkXXXXX.dat file
                            if del_choice =="y": os.remove(each_dat)
                            break
                        else:
                            Block_Header(block_file, tx_in_csv, tx_out_csv, timestamp_info_csv)

                bar() 
    
    database = Database(c_dir)
    # create tables 
    db, cursor = database.create_tables()
    # load data into tables
    database.load_into_tables(db, cursor)
    database.readdress(db, cursor)

    # delete folder with blkXXXXX.dat files
    if del_choice =="y": shutil.rmtree(input_path)

    Paths.goodbye(c_dir)
