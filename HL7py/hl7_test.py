"""
The MIT License

Copyright (c) 2016 Ankhos Clinical Oncology Software

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
from HL7py.test_messages import *
from HL7py.parser import parse, MultiMessage, reverse_rep_ch




def run():
    base = parse(reverse_rep_ch(DATA))
    assert len(
        base.ORC_list) == 2, "Segment listing wrong. Check line endings for LF/CR inconsistencies."
    assert base.ORC.trans_date_time.hl7 == '201210170000'

    base = parse(reverse_rep_ch(DATA))

    assert base.ORC.OBR.OBX_list[0].hl7 == 'OBX|1|NM|001347^Iron Bind.Cap.(TIBC)^L||476|ug/dL|250-450|H||N|F|||201210180726|BN'
    base.ORC.OBR.OBX_list[0].obs_id.label.data = "____MY LABEL___"
    assert base.ORC.OBR.OBX_list[0].hl7 == 'OBX|1|NM|001347^____MY LABEL___^L||476|ug/dL|250-450|H||N|F|||201210180726|BN',\
    "Can's assign one value."

    t = {'code': 'OBX', 'usr_def_access_chk': '', 'obs_dttm': None,
         'nature_of_abnormal_test': 'N',
         'probability': '', 'abnormal_flags': 'OMGWTH', 'producer_id': 'LOLWTH',
         'obs_results': '51', 'last_obs_normal_va_date': None,
         'obs_id': {'system_name': 'L', 'code': '100791',
                    'label': 'eGFR If NonAfricn Am'}, 'reference_range': '    >59',
         'value_type': 'NM', '_seg': 'OBX', 'units': 'mL/min/1.73', 'obs_sub_id': '',
         'obs_result_status': 'F', 'set_id': '4'}

    base = parse(reverse_rep_ch(DATA))
    assert base.ORC.OBR.OBX_list[2].hl7 == 'OBX|3|NM|001339^Iron, Serum^L||14|ug/dL|35-155'\
                     '|L||N|F|||201210180726|BN'
    base.ORC.OBR.OBX_list[2].data = t
    assert base.ORC.OBR.OBX_list[2].hl7 == 'OBX|4|NM|100791^eGFR If NonAfricn Am^L||51'\
                                           '|mL/min/1.73|    >59|OMGWTH||N|F||||LOLWTH',\
                                           "Cant assign multiple values by dictionary."

    #Confirm that MultiMessage correctly parses multiple messages in same string.
    mm = MultiMessage(reverse_rep_ch(DATA))
    assert len(mm.messages) == 1,"MultiMessage cannot handle message with only one MSH"
    assert mm.messages[0].PID.pat_name.hl7 == mm.messages[0].PID.pat_name.hl7


if __name__ == '__main__':
    run()
