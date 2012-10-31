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
import pprint
import HL7py.constants as constants
from HL7py.constants import *
from HL7py.hl7fields import hl7fields as hl7fieldspec
from HL7py.test_messages import *
import datetime



def rep_ch(s):
    """
    DEBUG ONLY!
    Helper function to display exactly the characters in a message for some terminals and
    editors which don't like to display \r much.  This also allows you to be explicit
    about which characters are where when debugging.
    """
    return s.replace(FS,'<FS>').replace(VT,'<VT>').replace(LF,'<LF>'+LF).replace(CR,'<CR>'+CR)

def reverse_rep_ch(s):
    """
    DEBUG_ONLY
    Helper function for converting back from rep_ch(). The function rep_ch and reverse_rep_ch
    should not be used in production, as the strings '<FS>','<CR>','<LF>','<FS>' *MIGHT*
    actually appear in the message.
    """
    return s.replace(LF,'').replace(CR,'').replace('<FS>',FS).\
    replace('<VT>',VT).replace('<CR>',CR).replace('<LF>',LF )


def _to_data(data_type, val):
    """
    Attempt to coerce the value to the correct data type.
    """
    #TODO: Clean up time parsing.
    if not val:
        return None
    if data_type.strip() == 'timestamp':
        try:
            trial = datetime.datetime.strptime(val, constants.MINUTE_TIME_FORMAT)
            return trial
        except Exception, e:
            try:
                trial = datetime.datetime.strptime(val, constants.SECOND_TIME_FORMAT)
                return trial
            except Exception,e2:
                try:
                    trial = datetime.datetime.strptime(val, '%Y%m%d %H:%M:%S')
                    return trial
                except Exception,e2:
                    return val


    elif data_type.strip() == 'date':
        try:
            trial = datetime.datetime.strptime(val, constants.DATE_TIME_FORMAT)
            return trial
        except Exception, e:
            return None
    elif data_type == 'number':
        try:
            return float(val)
        except ValueError:
            return None
    else:
        return str(val)


def _to_str(data_type, val):
    if data_type == 'timestamp':
        try:
            return datetime.datetime.strftime(val, constants.MINUTE_TIME_FORMAT)

        except TypeError, te:
            if val == '':
                return ''
            return ''
    elif data_type == 'date':
        try:
            return datetime.date.strftime(val, constants.DATE_TIME_FORMAT)
        except:
            return ''
    else:
        if val == None:
            return ''
        return str(val)


class Node(object):
    """
    Construct a skeleton of a node tree to be filled in later by hl7 string or by data
    dict. The sf_dict (Subfield Dictionary) is specified in the hl7fields.py file which
    is a dictionary that describes the number, types and names of the subfields.
    Keep in mind that a subfield may have subfields of its own and that the order of each
    subfield list is important.

    This fields dictionary is constructed from the HL7 specs but the variable names are
    python-ized, e.g. The subfield "Family Name" has been translated to family_name when
    accessing the attribute.
    """
    def __init__(self, code='',delims = DEFAULT_DELIMS, delim_idx = 0, data_type='string', subfields=[],):
        self._value = None
        self._data_type = data_type
        self._child_delim = delims[delim_idx]
        self._code = code
        self._child_nodes = []
        for sf_dict in subfields:
            sf_dict.update({'delims':delims,'delim_idx':delim_idx + 1})
            self.add_node(Node(**sf_dict))

    def __repr__(self):
        return "<Node %s>" % (self._code,)


    def add_node(self, node):
        """
        Add a child node to this node and expose its code for attribute access.
        """
        self._child_nodes.append(node)
        self.__dict__[node._code] = node

    def set_from_str(self, s, delims=[], delim_idx=-1):
        """
        Takes a HL7-formatted string and parses it into sub-nodes. The child Nodes should
        already exist from when the Node was created, we are just putting data in them.
        Each time we set_from_str on a child node, we increment the delim_idx to get the
        correct delimiter for splitting the string.

        As delim_idx is incremented or decremented, it will point to the correct delimiter
        as determined by the four characters in the message after MSH.
        """


        #Leaf node
        if len(self._child_nodes) == 0:
            self._value = _to_data(self._data_type, s)
            return

        sub_vals = s.split(self._child_delim)
        for i, node in enumerate(self._child_nodes):
            try:
                node.set_from_str(sub_vals[i], delims, delim_idx + 1)
            except IndexError, ie:
                # This is the case where we have more nodes than values. This is OK per the
                # HL7 specs so set them to ''. will result in something like
                # ABC|1|3|3|7||||||||.
                node.set_from_str('')



    def _get_as_str(self):
        """
        Returns the hl7 format of this node and all sub-nodes.
        """
        if not self._child_nodes:
            return _to_str(self._data_type, self._value)

        child_strs = []
        for child in self._child_nodes:
            child_strs.append(child._get_as_str())
        return self._child_delim.join(child_strs)


    def _set_from_data(self, args):
        """
        arg is either a value or a dict. If it is a value, it assigns straight-away, if it is a dict,
        it does set_from_data for each subnode in the dict. It assumes
        the tree has been constructed in an order specified by HL7Fields module.
        """


        if args == None:
            self._value = None
            return
        if len(self._child_nodes) == 0:
            self._value = args
            return

        #If this node is not a leaf node,make sure we have a dict whose keys supposedly
        #match the names of subnodes.

        assert isinstance(args, dict), "Data for sub-nodes must be a dictionary."
        for node in self._child_nodes:
            try:
                node._set_from_data(args.get(node._code))
            except Exception, e:
                node._set_from_data(str(e))


    def _get_as_data(self):
        """Return the data for this node in list format (list of lists maybe)"""
        if len(self._child_nodes) == 0:
            return _to_data(self._data_type, self._value)
        else:
            sub_data = {}
            for node in self._child_nodes:
                sub_data[node._code] = node._get_as_data()
            return sub_data


    data = property(_get_as_data, _set_from_data)
    hl7 = property(_get_as_str)

    def fmt_tree(self, indent=''):
        print indent + self._code + '|' + str(self._value)
        indent += '  '
        for node in self._child_nodes:
            node.fmt_tree(indent)


class NTE():
    """
    HL7 is horrible enough to not make NTE segments unique or hierarchical, so we have to
    handle NTE segments as a special case. They can come after many segments as an addendum
    so we will make them be handled as a general case. This way, every segment could have
    access to one and only one NTE (consecutive, uninterrupted NTE segments are supposed
    to go together)
    """

    def __init__(self):
        self._segments = []

    def add_text(self, NTE_line):
        self._segments.append(NTE_line)

    def get_text(self):
        return '\n'.join([seg.comment.hl7 for seg in self._segments])

class Segment(object):
    """
    A segment is a line delimited by Carriage Return per HL7 specs. They begin with three
    upper-case characters and are separated by control characters, e.g.

    MSH|^~\&|1100|BN|OPTX|BN002234|201210180743||ORU^R01|0417|P|2.3
       ^
       This is the field separator specifier

    The fields are delimited by whatever the fourth character is in the message. The 5-7th
    characters determine the sub-field delimiters.  Each Segment object has a base Node
    which we will use to access data from and parse each of these lines.

    """

    def __init__(self, raw_text = '',code = '', delims=delims, strict=False, data = {}):
        '''
        A Segment can be constructed in two ways:

        1. Pass valid HL7 text with the argument raw_text. Ths will parse the message
         using the delimiters determined within the message. The segment's structure
         will be looked up by using the first three non-control characters of the message.

        2. Pass the three letter segment code (e.g. MSH, PID, OBX) along with a dictionary
         of data whose attributes match all or a subset of nodes in the segment structure.

         The segment structure can be found in the HL7Fields.py file.
        '''

        if not strict:
            self._raw_text = raw_text.strip()
        else:
            self._raw_text = raw_text
        self.code = self._raw_text.split(delims[0])[0]

        #Determine if we are creating this segment from HL7 text or from a dictionary.
        if not self._raw_text:
            self.code = code
        if not self.code:
            raise ValueError("Unable to find code in specified message.")
        self.child_segments = []
        self.parent_seg = None
        self.node = None
        self.NTE = ''
        if self.code == '___':
            return

        if self.code not in hl7fieldspec:
            raise Exception("Message code not in specification: '%s'" % (self.code,))

        self.node = Node(**hl7fieldspec.get(self.code))
        if raw_text == '':
            data_code = data.get('code')
            if self.code and \
               data_code and \
               self.code != data_code:
                raise ValueError("'code' attribute in data does not match "
                                 "'code' attribute in segment.")
            data.update({'code':self.code})
            self.data = data
        else:
            delim_idx = 0
            self.node.set_from_str(raw_text, delims, delim_idx)

    def add_to_NTE(self, NTE_line):
        """
        NTE segments are a special case. They always apply to the non-NTE segment that
        precedes them. This just keeps track of all the NTE segments that belong together
        and allows access to them with the .note property.
        """
        if not self.NTE:
            self.NTE = NTE()
        self.NTE.add_text(NTE_line)

    def _get_note(self):
        if self.NTE:
            return self.NTE.get_text()
        else:
            return ''

    def _get_recursive_hl7_list(self):
        """
        Get this segment and any children together as strings.
        """

        #this segment is always before its children.
        if self.node:
            result = [self.node.hl7]
        else:
            result = []
        for child in self.child_segments:
            result += child._get_recursive_hl7_list()
        return result

    def get_as_str(self):
        """
        Assemble list of strings generated by recursing through child segments and their
        subnodes.
        """
        hl7_list = self._get_recursive_hl7_list()
        if len(hl7_list) == 0:
            return ''
        elif len(hl7_list) == 1:
            return hl7_list[0]
        return LF.join(hl7_list)


    def __repr__(self):
        return self.code

    def add_child(self, segment):
        segment.parent_seg = self
        self.child_segments.append(segment)

    def fmt_tree(self, indent=''):
        """
        Prints the tree format of this node and all of its sub-nodes. Useful for debugging.
        """

        print indent, self.code
        for child in self.child_segments:
            child.fmt_tree(indent + '    ')



    def _set_from_data(self, data):
        self.node._set_from_data(data)

    def _get_as_data(self):
        return self.node._get_as_data()

    def _pp_data(self):
        return pprint.pformat(self.data)


    data = property(_get_as_data, _set_from_data)
    data_pp = property(_pp_data)
    hl7 = property(get_as_str)
    note = property(_get_note)



    def __getattr__(self, attr_name):
        # If this segment was accessed like ORC.OBR.OBX_3, get the third
        # OBX in this series.
        if re_index_accessor.match(attr_name):
            return self.child_segments[int(attr_name.split('_')[1])]

        # If this segment was accessed like ORC.OBR.OBX_list, get the list of OBX children.
        elif re_list_accessor.match(attr_name):
            result = []
            for child in self.child_segments:
                if child.code == attr_name.split('_list')[0]:
                    result.append(child)
            return result

        # Get the first child with matching segment code.
        for child_seg in self.child_segments:
            if child_seg.code == attr_name:
                return child_seg

        # if there is no child segment of this code name, try going into the node which
        # contains the actual data of the segment.
        #if self.node:
        if attr_name == 'hl7':
            return self.get_as_str()
        return self.node.__getattribute__(attr_name)


class MultiMessage(object):
    """
    Parses a string that potentially has many Messages, separated by MSH. This class just
    abstracts out the parsing of MSH|(or whatever the field delimiter happens to be).
    """
    def __init__(self,string):
        substrings = re_MSH_split.split(string)
        self.messages = []
        for i,substr in enumerate(substrings):
            if substr.strip() == '':
                continue
            self.messages.append(parse('MSH' + substr))

class Message(object):
    """
    Message keeps track of the root Segment of the Segment/Node tree.
    """
    def __init__(self,base = None,raw_text=''):
        if not base:
            self._base = Segment('___|NONE')
        else:
            self._base = base
        self.raw_text = raw_text

    def __getattr__(self, item):
        return self._base.__getattr__(item)

    def _event_code(self):
        return self._base.MSH.msg_type.event_code.data

    def _message_code(self):
        return self._base.MSH.msg_type.messa
    def add_segment(self,seg):
        self._base.child_segments.append(seg)

    def add_segments(self,segments):
        for seg in segments:
            self.add_segment(seg)



def parse(raw_text):
    """
    Because of the way the HL7 spec is non-hierarchical, parsing a message depends on
    order of lines and an implicit hierarchy in relation to the segment code types. For
    example, it is implied that PID and ORC segments are at the same semantic level,
    and that a NTE segment can only show up after an OBX segment.  These rules are codified
    here in the constants.LEVELS dictionary.  The following assumptions are made in this parser:

    1.The lines in the message are in the correct order.
    2.The lines in the message adhere to the correct hierarchy (e.g. OBX is always after
     an OBR and ORC is always a base-level segment).

    As we iterate through lines in the message, we have a decision to make; do we

    1. Add the line as a sibling?
    2. Add the line as a child?
    3. Pop down the stack and add as sibling or child of a lower-level segment?
    4. Encounter a NTE segment and put it with whatever the most recent segment is.

    """

    base = Segment('___|NONE')

    last_seg = base #pointer to base; Don't change base directly.
    last_level = 0


    #Some segments may have Line Feed instead of Carriage Return (CR is the standard though)
    lines = raw_text.split(CR)
    if FALL_BACK_TO_LF and len(lines) == 1:
        lines = raw_text.split(LF)

    for line in lines:
        line = line.strip()
        if constants.REMOVE_VT:
            line = line.replace(VT, '')

        if line.strip() in ['', FS]:
            continue
        if 'MSH' == line[0:3]:
            delims = get_delims(line) #Delimiters could be different for every message.

        new_seg = Segment(line, delims=delims)
        if 'NTE' == line[0:3]:
            last_seg.add_to_NTE(new_seg)
            continue #NTE is special case, it should not affect stack/tree traversal ever.

        new_level = LEVELS.get(new_seg.code)
        assert new_level, "Missing level for code '%s'" % (new_seg.code)
        assert isinstance(new_level, int), "Invalid level for code '%s'. "\
                                           "Value must be an int." % (new_seg.code)

        #--Case 3--
        #Children are going home to live with ancestors. Set last_seg to the parent of the
        #parent of the pare...[ad nauseum] -  Do this 'level_difference' times. This is akin
        # to popping off of a stack but we don't actually want to pop things.
        if new_level < last_level:

            level_difference = last_level - new_level
            for i in range(0, level_difference):
                last_seg = last_seg.parent_seg

            last_seg.parent_seg.add_child(new_seg)
            last_seg = new_seg
            last_level = LEVELS.get(new_seg.code)

        #--Case 2--
        #New first child, need to increase our level indicator so that we know whether to
        # add a sibling or a child on the next line. This is akin to a push operation
        elif new_level > last_level:
            last_seg.add_child(new_seg)
            last_seg = new_seg
            last_level = LEVELS.get(last_seg.code)

        #--Case 1--
        #New sibling of last node, let the parent node know. This is analagous to an append.
        elif new_level == last_level:
            last_seg.parent_seg.add_child(new_seg)
            last_seg = new_seg
            last_level = LEVELS.get(last_seg.code)

    return Message(base,raw_text)


def get_delims(msh):
    #return {'field':msh[3],'component':msh[4],'subcomp':msh[5],'reptn':msh[6],'escape':msh[7]}
    return [msh[3], msh[4], msh[5], msh[6], msh[7]]

if __name__ == '__main__':
    run()
