import numpy as np
from io import BytesIO
from control import *

def getc(buffer):
    try:
        c = ord(buffer.read(1))
    except:
        c = -1
    return c
    
def putc(char, buffer):
    buffer.write(chr(char))
    return
    
def fwrite(buffer, size, n, outfile):
    _bytearray = bytearray( )
    outfile.write(_bytearray[0:size*n])
    return
    
def compress_yukes_bpe(data, BLOCKSIZE=2048, HASHSIZE=4096, MAXCHARS=200, THRESHOLD=3):
    compressed_data = compress_bpe(data, BLOCKSIZE, HASHSIZE, MAXCHARS, THRESHOLD)
    return "BPE \x00\x01\x00\x00%s%s%s" % (int_to_string(len(compressed_data), 4), int_to_string(len(data), 4), compressed_data)
    
def compress_bpe(data, BLOCKSIZE=2048, HASHSIZE=4096, MAXCHARS=200, THRESHOLD=3):
    buffer = np.zeros(BLOCKSIZE, dtype='uint8')
    leftcode = np.zeros(256, dtype='uint8')
    rightcode = np.zeros(256, dtype='uint8')
    left = np.zeros(HASHSIZE, dtype='uint8')
    right = np.zeros(HASHSIZE, dtype='uint8')
    count = np.zeros(HASHSIZE, dtype='uint8')
    size = 0
    infile = BytesIO(data)
    outfile = BytesIO()
    compress( infile, outfile, BLOCKSIZE, HASHSIZE, MAXCHARS, THRESHOLD, buffer, leftcode, rightcode, left, right, count, size)
    return outfile.getvalue()
    
def lookup(a, b ,hs, buffer, leftcode, rightcode, left, right, count, size):
    index = (a ^ (b << 5)) & (hs - 1)
    while ((left[index] != a or right[index] != b) and count[index] != 0):
        index = (index + 1) & (hs - 1)
    left[index] = a
    right[index] = b
    return index
    
def dataread(input, bs, hs, mc, buffer, leftcode, rightcode, left, right, count, size):
    used = 0
    
    for c in range(0, hs):
        count[c] = 0
    for c in range(0, 256):
        leftcode[c] = c
        rightcode[c] = 0
    size = 0
    
    while (size < bs and used < mc):
        c = getc(input)
        if c == -1:
            break
            
        if size > 0:
            index = lookup(buffer[size-1], c, hs, buffer, leftcode, rightcode, left, right, count, size)
            if count[index] < 255:
                count[index] += 1
        buffer[size] = c
        size += 1
        
        if (rightcode[c] == 0):
            rightcode[c] = 1
            used += 1
    return c == -1       
    
def datawrite(output, buffer, leftcode, rightcode, left, right, count, size):
    c = 0
    while (c < 256):
        if c == leftcode[c]:
            _len = 1
            c += 1
            while (_len < 127 and c < 256 and c == leftcode[c]):
                _len += 1
                c += 1
            putc(_len + 127, output)
            _len = 0
            if c == 256:
                break
        else:
            _len = 0
            c += 1 
            while ((_len < 127 and c < 256 and c != leftcode[c]) or (_len < 125 and c < 254 and (c+1) != leftcode[c+1])):
                _len += 1
                c += 1
            putc(_len, output)
            c -= _len + 1
        for i in range(0, _len+1):
            putc(leftcode[c], output)
            if c != leftcode[c]:
                putc(rightcode[c], output)
            c += 1
    putc(size % 256, output)
    putc(size / 256, output)
    fwrite(buffer, size, 1 , output)
    return
    
def compress(infile, outfile, bs, hs, mc, th, buffer, leftcode, rightcode, left, right, count, size):
    leftch = 0
    rightch = 0
    done = 0
    while (done == 0):
        done = dataread(infile, bs, hs, mc, buffer, leftcode, rightcode, left, right, count, size)
        code = 256
        while True:
            code -= 1
            for x in range(code, -1, -1):
                if code == leftcode[code] and rightcode[code] == 0:
                    break
            if code < 0:
                break
            best = 2
            for index in range(0, hs):
                if count[index] > best:
                    best = count[index]
                    leftch = left[index]
                    rightch = right[index]
            if best < th:
                break
            oldsize = size - 1
            w = 0
            for r in range(0, oldsize):
                if buffer[r] == leftch and buffer[r+1] == rightch:
                    if r > 0:
                        index = lookup(buffer[w-1], leftch, hs, buffer, leftcode, rightcode, left, right, count, size)
                        if count[index] > 1:
                            count[index] -= 1
                        index = lookup(buffer[w-1], code, hs, buffer, leftcode, rightcode, left, right, count, size)
                        if count[index] < 255:
                            count[index] += 1
                    if r < oldsize - 1:
                        index = lookup(rightch, buffer[r+2], hs, buffer, leftcode, rightcode, left, right, count, size)
                        if count[index] > 1:
                            count[index] -= 1
                        index = lookup(code, buffer[r+2], hs, buffer, leftcode, rightcode, left, right, count, size)
                        if count[index] < 255:
                            count[index] += 1
                    buffer[w] = code
                    w += 1
                    r += 1 
                    size -= 1
                else:
                    buffer[w] = buffer[r]
                    w += 1
                   
                buffer[w] = buffer[r]    

                leftcode[code] = leftch
                rightcode[code] = rightch
        
                index = lookup(leftch, rightch, hs, buffer, leftcode, rightcode, left, right, count, size)
                count[index] = 1            
            
        datawrite(outfile, buffer, leftcode, rightcode, left, right, count, size)
    return                    