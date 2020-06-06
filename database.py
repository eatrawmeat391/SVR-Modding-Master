from flask import session
import sqlite3
from pac import *
import os
from str_op import *
import tempfile 

class PAC_DB(object):
    _POSTFIX = "_pac"    
    def __init__(self, user_id, db_name=None):
        self.user_id = user_id
        if db_name is None:
            temp_file = tempfile.NamedTemporaryFile()        
            self.db_name = temp_file.name
        
            del temp_file
        else:
            self.db_name = db_name
            self.existing_db()
        
    def existing_db(self):
        self.conn   = sqlite3.connect(self.db_name)
        
    def create_db(self, pac_file_obj, filename):
        self.filename = filename
        
        self.conn   = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        
        pac_filename = os.path.basename(filename)
        
        self.cursor.execute('''CREATE TABLE pac_types     (id int, type string)''')
        
        self.cursor.execute('''INSERT INTO  pac_types VALUES (?, ?)''', (0, "PAC"))
        self.cursor.execute('''INSERT INTO  pac_types VALUES (?, ?)''', (1, "PACH"))
        self.cursor.execute('''INSERT INTO  pac_types VALUES (?, ?)''', (2, "DPAC"))
        self.cursor.execute('''INSERT INTO  pac_types VALUES (?, ?)''', (3, "EPAC"))
        self.cursor.execute('''INSERT INTO  pac_types VALUES (?, ?)''', (4, "DPK8"))
        self.cursor.execute('''INSERT INTO  pac_types VALUES (?, ?)''', (5, "EPK8"))
        
        self.cursor.execute('''CREATE TABLE pac_metadatas (filename text, pac_type_id int, 
        CONSTRAINT fk_pac_types FOREIGN KEY (pac_type_id) REFERENCES pac_types(id))
        ''')
        
        self.cursor.execute('''INSERT INTO  pac_metadatas VALUES (?, ?)''', (pac_filename, 0))
        
        self.cursor.execute('''CREATE TABLE pac_tocs      (file_no int, data blob) ''')                
        
        self.pac_file = PAC(pac_file_obj, 1)
        
        for i, toc in enumerate(self.pac_file.the_toc):
            file_no  = toc[0]
            file_data = self.pac_file.read(i)
            self.cursor.execute('''INSERT INTO  pac_tocs VALUES (?, ?)''', (file_no, file_data))
         
        self.conn.commit()
        
        