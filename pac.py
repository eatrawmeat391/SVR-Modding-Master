#!/usr/bin/python
from control import *
import os
from os import walk
from str_op import *

def log_int(n, base=10):
    if n == 0:
       raise ArithmeticError
    res = 0
    while n != 0:
        n /= base
        res += 1
    return (res - 1)
class PAC(object):
    def __init__(self, filename, name_id=0):
        self.file     = pac_file(filename)
        self.filename = self.file.filename
        # Get number of entry:
        self.type = self.file.read_string(4)
        if self.type == b"PAC ":
            self.name_size   = 2
            self.offset_size = 3
            self.size_size   = 3
        elif self.type == b"PACH":
            self.name_size   = 4
            self.offset_size = 4
            self.size_size   = 4
        self.file.seek(0x04)
        self.entry = self.file.read_int(0x04)
        # Get PAC toc
        self.the_toc = [] # fileno, file_address, file_size
        # 01 00 - 48 08 00 - F0 28 00
        for x in range(0, self.entry):
            _fileno = self.file.read_int(self.name_size)
            _address= self.file.read_int(self.offset_size)
            _size   = self.file.read_int(self.size_size)
            self.the_toc.append((_fileno, _address, _size))
            
        self.file_address = self.file.tell()
        self.name_id = name_id
        # find duplicated entry
        self.duplicated_dict = {}
        file_no_list = [toc[0] for toc in self.the_toc]
        for _fileno in file_no_list:
            if _fileno in self.duplicated_dict:
                continue
            count = file_no_list.count(_fileno)
            if count > 1:
                self.duplicated_dict[_fileno] = [i for i, n in enumerate(file_no_list) if n == _fileno]
                        
    def is_dir(self, index):
        return False
        
    def get_file_extension(self, index):
        _fileno, _address, _size = self.the_toc[index]
        _real_addr = _address + self.file_address
        self.file.seek(_real_addr)
        _data = self.file.read_string(4)
        return string_get_file_extension(_data)    
        
    def get_file_name(self , index):
        if self.name_id == 0: # file will be named according to their order
            return "file%.6d" % index
        elif self.name_id == 1: # file will be named according to their ID
            if self.the_toc[index][0] == 0:
                digits = 1
            else:
                digits = log_int(self.the_toc[index][0], 16) + 1
            if digits % 2 == 1:
                digits += 1
            name = "%.*X" % (digits, self.the_toc[index][0])                
            if self.the_toc[index][0] in self.duplicated_dict:
                name = "%s[%d]" % (name, self.duplicated_dict[self.the_toc[index][0]].index(index))
            return name
            
            
        elif self.name_id == 2: # Same as 1 except the minimum digits is 4
            if self.the_toc[index][0] == 0:
                digits = 1
            else:
                digits = log_int(self.the_toc[index][0], 16) + 1
            if digits % 2 == 1:
                digits += 1            
            if digits < 4:
                digits = 4
            name = "%.*X" % (digits, self.the_toc[index][0])                
            if self.the_toc[index][0] in self.duplicated_dict:
                name = "%s[%d]" % (name, self.duplicated_dict[self.the_toc[index][0]].index(index))
            return name
            
    def get_file_address(self, index):
        return self.the_toc[index][1] + self.file_address
        
    def get_file_size(self, index):
        return self.the_toc[index][2]
        
    def filename_to_index(self, filename):
        filename = filename.lower()
        for x in range(0, self.entry):
            file = self.get_file_name(x)
            extension = self.get_file_extension(x)
            x_filename = "%s%s" % (file, extension)
            x_filename = x_filename.lower()
            if filename == x_filename or filename == ("%s.dat" % file):
                return x
        return -1
                
        
    def read(self, filename):
        try:
            index = int(filename)
        except:
            index = self.filename_to_index(filename)
        if index == -1:
            raise IOError
        else:
            _fileno,_address,_size = self.the_toc[index]
            _real_addr = _address + self.file_address
            self.file.seek(_real_addr)
            _data      = self.file.read_string(_size)
        return _data
    
         
    
    def namelist(self):
        f = []
        for x in range(0, self.entry):
            file = self.get_file_name(x)
            extension = self.get_file_extension(x)
            f.append("%s%s" % (file, extension))
        return f

    def extract_info(self, _filename=None):
        if _filename is None:
            _filename = "%s_info.txt" % self.filename
        with open(_filename, 'w') as output:
            for x in range(self.entry):
                file_no, unused, unused = self.the_toc[x]
                if self.type == 'PAC ':
                    output.write("ID: %.4X, %s%s\n" % (file_no,self.get_file_name(x), self.get_file_extension(x))) 
                else:
                    output.write("ID: %.8X, %s%s\n" % (file_no,self.get_file_name(x), self.get_file_extension(x))) 
        return
           
    def extract_file(self, index, _filename=None, is_gui=False):
        if _filename is None:
           _dirname = '@%s\\' % self.filename 
           if not os.path.exists(_dirname):
                os.makedirs(_dirname)
           _extension = self.get_file_extension(index)
           _filename = "%s%s%s" % (_dirname, self.get_file_name(index), _extension)
        _fileno,_address,_size = self.the_toc[index]
        with open(_filename, 'wb+') as output:
            _real_addr = _address + self.file_address
            self.file.seek(_real_addr)
            _data      = self.file.read_string(_size)
            output.write(_data)
        #if is_gui == False:
             #print "File extracted: %r" % _filename
        return
    
    def extract_all(self,is_gui=False,_dirname=None):
        if _dirname is None:
            _dirname = '@%s\\' % self.filename 
        if not os.path.exists(_dirname):
            os.makedirs(_dirname)        
        for x in range(0, self.entry):
            _name = self.get_file_name(x)
            _extension = self.get_file_extension(x)
            _filename  = _dirname + _name + _extension
            self.extract_file(x, _filename,is_gui)
        return
        
    def extract_all_memory(self, is_gui=False):
        mem_files = memory_file()
        for x in range(0, self.entry):
            _name = self.get_file_name(x)
            _extension = self.get_file_extension(x)
            _filename = _name + _extension
            _data = self.read(_filename)
            mem_files.add_file(_filename, _data)
        return mem_files

    def rebuild_all_memory(self, is_gui=False, mem_files=memory_file()):
        _temp1= open('tmp\\temp1', 'wb')
        _temp2= open('tmp\\temp2', 'wb')
        
        _entry_data = self.file.int_to_string(self.entry, 4)
        _temp1.write(self.type)
        _temp1.write(_entry_data)
        _addr      = 0
        for x in range(0, self.entry):
            _filename  = self.get_file_name(x)
            _extension = self.get_file_extension(x)
            try:
                _path      = "%s%s" % (_filename, _extension)                            
                _file         = pac_file(mem_files.file_dict[_path])
            except KeyError:
                _path      = "%s.dat" % (_filename)                            
                _file         = pac_file(mem_files.file_dict[_path])
            _size      = _file.size
            _data         = _file.read_string(_size)
            #if is_gui == False:
                 #print "Step %d: Processing file %s%s" % (x,_filename, _extension)
            _useless_data = '\x00'* ((4 - _size % 4) if _size % 4 != 0 else 0)
            _useless_size = len(_useless_data)
            _temp2.write(_data)
            _temp2.write(_useless_data)
            
            _fileno, _unused, _unused1    = self.the_toc[x]      
            #if is_gui == False:
                #print "- Data starts at 0x%.6X" % (_addr)
                #print "- Size 0x%.4X bytes" % (_size)                              
            _fileno_data = self.file.int_to_string(_fileno, self.name_size)            
            _addr_data   = self.file.int_to_string(_addr, self.offset_size)
            _size_data   = self.file.int_to_string(_size, self.size_size)
            _temp1.write(_fileno_data)
            _temp1.write(_addr_data)
            _temp1.write(_size_data)
            _addr        = _addr + _size + _useless_size
            
            del _file
            mem_files.close(_path)
        _temp1.close()
        _temp2.close()
        # merge 2 file into one
        _temp1 = pac_file('tmp\\temp1')
        _temp2 = pac_file('tmp\\temp2')
        _data1 = _temp1.read_string(_temp1.size)
        _data2 = _temp2.read_string(_temp2.size)
        with open('%s-NEW' % self.filename, 'wb') as output:
            output.write(_data1)
            output.write(_data2)
            _total_size = output.tell()
            output.write("\x00"*((0x800 - _total_size % 0x800) if _total_size % 0x800 != 0 else 0))
        
        del _temp1
        del _temp2
        os.remove('tmp\\temp1')
        os.remove('tmp\\temp2')
        return

    def rebuild(self, is_gui=False,dirname=None):
        if dirname is None:
            dirname = '@%s\\' % self.filename
        _temp1= open('tmp\\temp1', 'wb')
        _temp2= open('tmp\\temp2', 'wb')
        
        _entry_data = self.file.int_to_string(self.entry, 4)
        _temp1.write(self.type)
        _temp1.write(_entry_data)
        _addr      = 0
        for x in range(0, self.entry):
            _filename  = self.get_file_name(x)
            _extension = self.get_file_extension(x)
            try:
                _path      = "%s%s%s" % (dirname,_filename,_extension)            
                _file         = pac_file(_path)
            except IOError:
                _path      = "%s%s.dat" % (dirname,_filename)                            
                _file         = pac_file(_path)
            _size      = os.path.getsize(_path)
            _data         = _file.read_string(_size)
            #if is_gui == False:
                 #print "Step %d: Processing file %s%s" % (x,_filename, _extension)
            _useless_data = '\x00'* ((4 - _size % 4) if _size % 4 != 0 else 0)
            _useless_size = len(_useless_data)
            _temp2.write(_data)
            _temp2.write(_useless_data)
            
            _fileno, _unused, _unused1    = self.the_toc[x]      
            #if is_gui == False:
                #print "- Data starts at 0x%.6X" % (_addr)
                #print "- Size 0x%.4X bytes" % (_size)                              
            _fileno_data = self.file.int_to_string(_fileno, self.name_size)            
            _addr_data   = self.file.int_to_string(_addr, self.offset_size)
            _size_data   = self.file.int_to_string(_size, self.size_size)
            _temp1.write(_fileno_data)
            _temp1.write(_addr_data)
            _temp1.write(_size_data)
            _addr        = _addr + _size + _useless_size
            
            del _file
        _temp1.close()
        _temp2.close()
        # merge 2 file into one
        _temp1 = pac_file('tmp\\temp1')
        _temp2 = pac_file('tmp\\temp2')
        _data1 = _temp1.read_string(_temp1.size)
        _data2 = _temp2.read_string(_temp2.size)
        with open('%s-NEW' % self.filename, 'wb') as output:
            output.write(_data1)
            output.write(_data2)
            _total_size = output.tell()
            output.write("\x00"*((0x800 - _total_size % 0x800) if _total_size % 0x800 != 0 else 0))
        
        del _temp1
        del _temp2
        os.remove('tmp\\temp1')
        os.remove('tmp\\temp2')
        return
