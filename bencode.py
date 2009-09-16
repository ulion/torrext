
import re
try:
    import psyco # Optional, 2.5x improvement in speed
    psyco.full()
except ImportError:
    pass

decimal_match = re.compile('\d')

################################################################################
# Bencode encoding code by Petru Paler, slightly simplified by uriel
from types import StringType, IntType, LongType, DictType, ListType, TupleType, BooleanType

#class Bencached(object):
#    __slots__ = ['bencoded']
#
#    def __init__(self, s):
#        self.bencoded = s

#def encode_bencached(x,r):
#    r.append(x.bencoded)

def encode_int(x, r):
    r.extend(('i', str(x), 'e'))

def encode_string(x, r):
    r.extend((str(len(x)), ':', x))

def encode_list(x, r):
    r.append('l')
    for i in x:
        encode_func[type(i)](i, r)
    r.append('e')

def encode_dict(x,r):
    r.append('d')
    ilist = x.items()
    ilist.sort()
    for k, v in ilist:
        r.extend((str(len(k)), ':', k))
        encode_func[type(v)](v, r)
    r.append('e')

encode_func = {}
#encode_func[type(Bencached(0))] = encode_bencached
encode_func[IntType] = encode_int
encode_func[LongType] = encode_int
encode_func[StringType] = encode_string
encode_func[ListType] = encode_list
encode_func[TupleType] = encode_list
encode_func[DictType] = encode_dict
encode_func[BooleanType] = encode_int

def bencode(x):
    r = []
    encode_func[type(x)](x, r)
    return ''.join(r)

def test_bencode():
    assert bencode(4) == 'i4e'
    assert bencode(0) == 'i0e'
    assert bencode(-10) == 'i-10e'
    assert bencode(12345678901234567890L) == 'i12345678901234567890e'
    assert bencode('') == '0:'
    assert bencode('abc') == '3:abc'
    assert bencode('1234567890') == '10:1234567890'
    assert bencode([]) == 'le'
    assert bencode([1, 2, 3]) == 'li1ei2ei3ee'
    assert bencode([['Alice', 'Bob'], [2, 3]]) == 'll5:Alice3:Bobeli2ei3eee'
    assert bencode({}) == 'de'
    assert bencode({'age': 25, 'eyes': 'blue'}) == 'd3:agei25e4:eyes4:bluee'
    assert bencode({'spam.mp3': {'author': 'Alice', 'length': 100000}}) == 'd8:spam.mp3d6:author5:Alice6:lengthi100000eee'
    #assert bencode(Bencached(bencode(3))) == 'i3e'
    try:
        bencode({1: 'foo'})
    except TypeError:
        return
    assert 0

################################################################################

def bdecode(data):
    '''Main function to decode bencoded data'''
    chunks = list(data)
    chunks.reverse()
    root = _dechunk(chunks)
    return root

def _dechunk(chunks):
    item = chunks.pop()

    if (item == 'd'): 
        item = chunks.pop()
        hash = {}
        while (item != 'e'):
            chunks.append(item)
            key = _dechunk(chunks)
            hash[key] = _dechunk(chunks)
            item = chunks.pop()
        return hash
    elif (item == 'l'):
        item = chunks.pop()
        list = []
        while (item != 'e'):
            chunks.append(item)
            list.append(_dechunk(chunks))
            item = chunks.pop()
        return list
    elif (item == 'i'):
        item = chunks.pop()
        num = ''
        while (item != 'e'):
            num  += item
            item = chunks.pop()
        return int(num)
    elif (decimal_match.findall(item)):
        num = ''
        while decimal_match.findall(item):
            num += item
            item = chunks.pop()
        line = ''
        for i in range(1, int(num) + 1):
            line += chunks.pop()
        return line
    raise "Invalid input!"