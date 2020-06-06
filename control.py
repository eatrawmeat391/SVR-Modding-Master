#!/usr/bin/python
import struct
import binascii
import os 
from io import BytesIO

def int_to_string(number,size):
    size = size * 2        
    b = "%.*X" % (size, number)
    b = binascii.unhexlify(b)
    b = b[::-1]
    return b
    
class pac_file(object):
    def __init__(self, filename, buffer=2048):
        if hasattr(filename, 'read') and hasattr(filename, 'seek'):
            self.the_file = filename
            self.the_file.seek(0)
            self.size = len(self.the_file.read())
            self.the_file.seek(0)
            self.filename = ''
        else:
            self.the_file = open(filename, 'rb')
            self.size     = os.path.getsize(filename)
            self.filename = filename
        self.buffer   = buffer
        
    def close(self):
        self.the_file.close()
        
    def tell(self):
        return self.the_file.tell()
    
    def rewind(self):
        self.the_file.rewind()
        
    def seek(self, offset, whence=0):
        self.the_file.seek(offset, whence)

    #def write(self,str):
    #    self.the_file.write(str)
        
    def read_int(self, size):
       string   = self.the_file.read(size)
       string   = string[::-1]
       hex_data = binascii.hexlify(string)
       #if sys.byteorder == 'little':
       return int(hex_data, 16)
       
    def read_string(self, size):
        no_chunk = size // self.buffer
        remain_s = size - (no_chunk * self.buffer)
        buf = BytesIO()
        for i in range(0, no_chunk):
            data = self.the_file.read(self.buffer)
            buf.write(data)
        data = self.the_file.read(remain_s)
        buf.write(data)
        #if sys.byteorder == 'little'
        return buf.getvalue()

    def int_to_string(self, number,size):
        size = size * 2        
        b = "%.*X" % (size, number)
        b = binascii.unhexlify(b)
        b = b[::-1]
        return b
        
class memory_file(object):
    def __init__(self, fileobj_list=()):
        self.file_dict = {}
        for fileobj in fileobj_list:
            offset = fileobj.tell()
            fileobj.seek(0)
            data = fileobj.read()
            fileobj.seek(offset)
            self.file_dict[fileobj.name] = BytesIO(data)
        return
        
    def add_file(self, filename, data):
        self.file_dict[filename] = BytesIO(data)
        return
   
    def remove_file(self, filename):
        del self.file_dict[filename]
        return
        
    def getvalue(self, filename):
        offset = self.file_dict[filename].tell()
        self.file_dict[filename].seek(0)
        data = self.file_dict[filename].read()
        self.file_dict[filename].seek(offset)
        return data
        
    def read(self, filename):
        return self.file_dict[filename].getvalue()
    
    def get_fileobj(self, filename):
        return self.file_dict[filename]
        
    def namelist(self):
        list = []
        for x in self.file_dict:
            list.append(x)
        return list

    def close(self, filename):
        self.file_dict[filename].close()