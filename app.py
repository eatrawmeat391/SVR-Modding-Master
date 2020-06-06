from flask import Flask, render_template, request, session
import os
import json
from tkinter import Tk
from pac import *
from io import BytesIO
import uuid
from database import *

app = Flask(__name__)


# extra file to watch
extra_dirs = ['static/']
extra_files = extra_dirs[:]
for extra_dir in extra_dirs:
    for dirname, dirs, files in os.walk(extra_dir):
        for filename in files:
            filename = os.path.join(dirname, filename)
            if os.path.isfile(filename):
                extra_files.append(filename)

@app.route('/')
def index():
    session['is_file_open'] = False
    if not "user_id" in session:
        session['user_id'] = str(uuid.uuid4())
    return render_template("main.html")

def remove_db(db_name):
    infile = open(db_name, 'rb')
    signature = infile.read(13)
    infile.close()

    if signature == b"SQLite format":        
        os.remove(db_name)
    return
    
def read_pac_from_db(db_name):
    return_dict = []
    pac_db = PAC_DB(session['user_id'], db_name)
    cursor = pac_db.conn.execute("SELECT file_no, data from pac_tocs")
    row = []
    
    while row is not None:
        current_info = {}
        row = cursor.fetchone()
        if row is None:
            break
        file_no, data = row                
        try:
            extension = data[:4].split(b' ')[0].split(b'\x00')[0].decode("ASCII")
        except:
            extension = "DAT"
        current_info   = [file_no,extension, len(data)]
        return_dict.append(current_info)
    return return_dict
    
@app.route('/load_existing_pac/', methods=["POST"])
def load_pac_if_exist():    
    return_dict = []
        
    if request.method.upper() == "POST":
        return_dict = []
        if 'db_name' in session:
            return_dict = read_pac_from_db(session['db_name'])
    return json.dumps(return_dict)

@app.route('/rename_pac_slot/<old_slot>/<new_slot>', methods=["POST"])
def rename_pac_slot(old_slot, new_slot):
    return_dict = {}
         
    if request.method.upper() == "POST":
        if old_slot == new_slot:
            status = "fails";
            msg = "Old slots and New slots are the same";
            return_dict = {'status': status, 'msg': msg}
        else:
            if 'db_name' in session:
                pac_db = PAC_DB(session['user_id'], session['db_name'])
                cursor = pac_db.conn.cursor()
                
                cursor.execute('''SELECT file_no from pac_tocs WHERE file_no=? LIMIT 1''', (new_slot,))
                row = cursor.fetchone()
                if row is not None:
                    status = "fails"
                    msg = "New slots already exist"
                    return_dict = {'status': status, 'msg': msg}
                else:
                    cursor.execute('''UPDATE pac_tocs SET file_no=? WHERE file_no=?''', (new_slot, old_slot))                    
                    if cursor.rowcount >= 1:
                        pac_db.conn.commit()
                        status = "success"
                        msg = "Successfully rename the slot"
                        return_dict = {'status': status, 'msg': msg}
                    else:
                        status = "fails"
                        msg = "Cannot rename the slots, an unknown error"
                        return_dict = {'status': status, 'msg': msg}
    return json.dumps(return_dict)
@app.route('/open_pac/<filename>', methods=["POST"])
def open_pac(filename):
    #Tk().withdraw()
    
    return_dict = []
            
    if request.method.upper() == "POST":
        if request.headers['Content-Type'] == 'application/octet-stream':
            binary_data = request.data.split(b'\r\n', 4)[4][:-0x2E]                           
            pac_db = PAC_DB(session['user_id'])
            pac_db.create_db(BytesIO(binary_data), filename)
            
            # remove db_name if exist
            app.db_name.append(pac_db.db_name)
            if 'db_name' in session:
                remove_db(session['db_name'])
                app.db_name.remove(session['db_name'])
            
            session['db_name'] = pac_db.db_name            
            return_dict = read_pac_from_db(pac_db.db_name)
                            
    return json.dumps(return_dict)

def cleanup(self):
    try:
        for db_name in self.db_name:
            remove_db(db_name)
    except (AttributeError, IOError):
        pass
        
if __name__ == '__main__':
    app.secret_key = str(uuid.uuid4())
    app.config['SESSION_TYPE'] = 'filesystem'
    app.db_name = []
    try:
        app.run(debug=True, extra_files=extra_files)
    finally:
        cleanup(app)
    
