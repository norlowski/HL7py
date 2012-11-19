HL7py
=====
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

=====



A parser for the HL7 Health data interchange format written in python. Provides
attribute-like access to correct datatypes and provides the ability to construct HL7
messages from dictionaries.

The HL7 transport protocol is a confusing mess of pipes and carriage returns. This package
provides easy Pythonic access to attributes within a message. There is much domain
knowledge of segments names and field names, but what follows are some basic examples of
syntax and usage.



Here is a sample message from http://www.coast2coastinformatics.com/user/ADTA08_examples-110106.pdf
 
    MSH|^~\&|AccMgr|1|||20050110045504||ADT^A01|599102|P|2.3|||
    EVN|A01|20050110045502|||||
    PID|1||10006579^^^1^MRN^1||DUCK^DONALD^D||19241010|M||1|111 DUCK ST^^FOWL^CA^999990000^^M|1|8885551212|8885551212|1|2||40007716^^^AccMgr^VN^1|123121234|||||||||||NO NK1|1|DUCK^HUEY|SO|3583 DUCK RD^^FOWL^CA^999990000|8885552222||Y||||||||||||||
    PV1|1|I|PREOP^101^1^1^^^S|3|||37^DISNEY^WALT^^^^^^AccMgr^^^^CI|||01||||1|||37^DISNEY^WALT^^^^^^AccMgr^^^^CI|2|40007716^^^AccMgr^VN|4|||||||||||||||||||1||G|||20050110045253||||||
    GT1|1|8291|DUCK^DONALD^D||111^DUCK ST^^FOWL^CA^999990000|8885551212||19241010|M||1|123121234||||#Cartoon Ducks Inc|111^DUCK ST^^FOWL^CA^999990000|8885551212||PT| DG1|1|I9|71596^OSTEOARTHROS NOS-L/LEG ^I9|OSTEOARTHROS NOS-L/LEG ||A|
    IN1|1|MEDICARE|3|MEDICARE|||||||Cartoon Ducks Inc|19891001|||4|DUCK^DONALD^D|1|19241010|111^DUCK ST^^FOWL^CA^999990000|||||||||||||||||123121234A||||||PT|M|111 DUCK ST^^FOWL^CA^999990000|||||8291
    IN2|1||123121234|Cartoon Ducks Inc|||123121234A|||||||||||||||||||||||||||||||||||||||||||||||||||||||||8885551212 IN1|2|NON-PRIMARY|9|MEDICAL MUTUAL CALIF.|PO BOX 94776^^HOLLYWOOD^CA^441414776||8003621279|PUBSUMB|||Cartoon Ducks Inc||||7|DUCK^DONALD^D|1|19241010|111 DUCK ST^^FOWL^CA^999990000|||||||||||||||||056269770||||||PT|M|111^DUCK ST^^FOWL^CA^999990000|||||8291 IN2|2||123121234|Cartoon Ducks Inc||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||8885551212
    IN1|3|SELF PAY|1|SELF PAY|||||||||||5||1

 
(Lines not wrapped for emotional effect)


=================DATA ACCESS EXAMPLES============

You will be able to use syntax like

1. 'SEG.some_attribute.data' to access either a dictionary (if that field has subfields)
   or a value parsed to the correct datatype, e.g. datetime or numeric.
2. 'SEG.some_attribute.hl7' to have the message construct the HL7 equivalent of that
   attribute and all of its following segments and subsegments.

3. 'SEG.some_attribute.some_timestamp.data = datetime.datetime.now()' allows you to set
   the value of a specific note/segment. See examples in the tests.


Examples:

    from HL7py import parser
    my_message = parser.parse(incoming_str)
    my_message.PID.pat_name.data
    {'family_name':'DUCK','give_name':'DONALD','middle_name':'D'}
    my_message.PID.pat_name.family_name.hl7
    'DUCK'
    my_message.IN1[0].ins_company_name.hl7
    'MEDICARE'
    my_message.IN1[0].ins_company_name.data
    'MEDICARE'
    my_message.IN1[1].ins_company_name.hl7
    'SELF PAY'
    my_message.IN1_list
    [IN1,IN1]
    for ins in IN1_list:
        print ins.ins_company_name.hl7
    'MEDICARE'
    'SELFPAY




The NTE section is a special case. NTE sections can come after any other section and
are assembled into the .note attribute for a segment.



    PID|1|123456789|112233|1234567|Test^Patient||19820620|F|||123 Fake St.^^SumCity^ST^12345-||(123)456-7890||||||
    ORC|RE|29117637990^LAB|291176379902012^LAB||||||201210170000|||1366445686^Doctor^M^^^^^N
    OBR|1|29117637990^LAB|291176379902012^LAB|001321^Iron and TIBC^L|||201210171632|||||||201210171934||||M542856833||29117637990||201210180743|||F
    OBX|1|NM|001347^Iron Bind.Cap.(TIBC)^L||476|ug/dL|250-450|H||N|F|19840622||201210180726|BN
    OBX|2|NM|001348^UIBC^L||462|ug/dL|150-375|H||N|F|19940518||201210180726|BN
    NTE|1|L|Results confirmed on
    NTE|2|L|dilution.
    
The following would occur:

    print my_message.ORC.OBR.OBX_list[1].note
    'Results confirmed on dilution'

=================MESSAGE CREATION EXAMPLES============
Messages are created by assembling Segments and adding them to a Message.
 Here is an example of how our EMR, Ankhos, constructs an ADT/A08 message.  The chart.to_dict()
 method constructs a dictionary of the relevant fields from chart demographics, etc.

    msg = Message()
    msh_data= dict(
            recv_app={'app_name': 'Their App'},
            send_app={'app_name': 'ANKHOS'},
            msg_type=dict(message_code='ADT',
                          event_code='A08'),
            accept_ack_type='AL',
            application_ack_type='AL',
            proc_id='P',
            version='2.3',
            msg_ctl_id=control_id,
            encoding_chars='^~\&',
            timestamp=datetime.datetime.now())
    MSH = Segment(code='MSH',data=msh_data)
    evn_data = dict(event_code=event_code,timestamp=dict(time=datetime.datetime.now(),
                                                          resolution='S'))
    EVN = Segment(code='EVN',data=evn_data)
    PID = Segment(code='PID',data=chart.to_dict())
    pv1_data = {...}
    PV1 = Segment(code='PV1',data=pv1_data)
    msg.add_segments([MSH,EVN,PID,PV1])

    #Voila!
    print msg.hl7


As long as the data dictionaries follow the signatures in the HL7fields.py specification,
the Segments should be constructed correctly.  There are a LOT of HL7 specified segments
but only a few in the include HL7fields.py file. We simply haven't had a use for most of them
yet but if we do, I will be sure to update the HL7fields specification dictionary.


Current limitations:
 1. The ADD operation is not supported. (very low priority)
 2. Intra-field repetition is not yet supported
 3. The tests included are only smoke tests to make sure fundamental things haven't broken!
   HL7 is used in life-critical systems. Again. Please Please Please test your own software!
   More real tests will be added when time allows.
