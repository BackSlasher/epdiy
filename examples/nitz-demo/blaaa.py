import struct
from main import giraffe
chars = [struct.pack('B', c) for c in giraffe.gir]
chars = [b'\t' if c == b'\n' else c for c in chars]
s = b''.join(chars)
with open('giraffe-escaped.bin', 'wb') as f: f.write(s)


import base64
chars = [struct.pack('B', c) for c in giraffe.gir]
s = b''.join(chars)
s2 = base64.b64encode(s)
with open('giraffe-escaped.bin', 'wb') as f: f.write(s)

chars = [struct.pack('B', c) for c in giraffe.gir]
s = b''.join(chars)
with open('giraffe-escaped.bin', 'wb') as f: f.write(s)
