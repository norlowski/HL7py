"""
The MIT License

Copyright (c) 2012 Nicholas Orlowski

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""
import re
CR = chr(0x0d)# '\r'
FS = chr(0x1C)# file separator
LF = chr(0x0a)# '\n'
VT = chr(0x0b)# vertical tab


DATE_TIME_FORMAT = '%Y%m%d'
MINUTE_TIME_FORMAT = '%Y%m%d%H%M'
SECOND_TIME_FORMAT = '%Y%m%d%H%M%S'

LEVELS =\
{'BASE': 0, 'MSH': 1, 'PID': 1, 'ORC': 1, 'OBR': 2, 'MFI':1,'MFE':1,'STF':1,'PRA':1,
 'OBX': 3, 'ZPS': 1, 'PV1': 1, 'EVN': 1,'NTE':4,'MSA':1,
 'IN1': 1, 'IN2': 1, 'PD1': 1, 'NK1': 1, 'ZBI': 1, 'GT1': 1,'FTS':1}

REMOVE_VT = True
FALL_BACK_TO_LF = True
#Default delimiters, may be switched upon parsing of MSH segment
#DEFAULT_DELIMS = {'field':'|','component':'^','subcomp':'&','reptn':'~','escape':'\\'}
delims = ['|','^','&','~','\\']
DEFAULT_DELIMS = delims

re_index_accessor = re.compile(r'^\w{3}_\d$')
re_list_accessor = re.compile(r'^\w{3}_list$')
re_MSH_split = re.compile("(^|[\n\r\f\t\v])MSH")
