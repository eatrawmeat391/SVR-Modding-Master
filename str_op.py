from io import BytesIO, StringIO
def string_fix(string):
    buf = StringIO()
    i = 0
    forbidden_char = ['<','>',':','\"','/','\\','|', '?','*']
    forbidden_path = ['CON', 'PRN','AUX','COM1','COM2','COM3','COM4','COM5','COM6','COM7','COM8','COM9',
    'LPT1','LP2','LPT3','LPT4','LPT5','LPT6','LPT7','LPT8','LPT9']
    for char in string:
        c = ord(char)        
        if c in range(0, 0x20+1) or c not in range(21, 128) or char in forbidden_char:
            if char != "\\" and i != (len(string) - 1):
                buf.write("{%.2X}" % c)
        else:
            buf.write(char)
        i += 1
    output_string = buf.getvalue()
    for path in forbidden_path:
        if output_string == path:
            return "{%s}" % output_string
    return output_string
    
def is_string_invalid(string):
    for char in string:
        c = ord(char)
        if c in range(0, 0x20) or c not in range(20, 128):
            return True
    return False
    
def string_get_file_extension(_data):
    if _data == b"PAC " or _data == b"PACH" or _data == b"DPAC" or _data == b"EPAC" or _data == b"HSPC" or _data == b"SHDC":
        return ".pac"
    elif _data == b"<?xm":
        return ".xml"
    elif _data == b"BPE ":
        return ".bpe"
    elif _data == b"\x1BLua":
        return ".lua"
    elif is_string_invalid(_data) == False:
        _data =  _data.lower()
        _data =  _data.replace(" ", "")
        symbol = ("!", "@", "#", "$", "%", "^", "&", "*", 
                  "(", ")", "-", "_", "=", "+", "|", "\\",
                  "/", "[", "]", "{", "}", ":", ";", "\"",
                  "\'", "<", ">", ",", ".", "/", "?", "~",
                  "`")  
        if len(_data) < 3:
            return ".dat"
        else:
            for char in symbol:
                if char in _data: 
                    return ".dat"
            return ".%s" % _data
    else:
        return ".dat"
