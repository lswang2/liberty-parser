from lark import Lark, Transformer, v_args
from .types import *

liberty_grammar = r"""
    ?start: group
    
    group: name group_args "{" [statement (statement)*] "}"
    group_args: "(" [name ("," name)*] ")"
    
    ?statement: group
        | attribute ";"
        | define ";"
        
    value: name
        | number -> number
        | number unit -> number_with_unit
        | numbers
        | string -> escaped_string
        
    numbers: "\"" [number ("," number)*] "\""
        
    unit: CNAME
        
    ?attribute: simple_attribute
        | complex_attribute
        
    simple_attribute: name ":" value
    
    complex_attribute: name "(" value ("," value)* ")"
        | name "(" name ("," name)* ")"
    
    define: "define" "(" value "," value "," value ")"
    
    name : CNAME
    string: ESCAPED_STRING
    
    number: SIGNED_NUMBER
    
    COMMENT: /\/\*(\*(?!\/)|[^*])*\*\//
    NEWLINE: /\\?\r?\n/
    
    %import common.WORD
    %import common.ESCAPED_STRING
    %import common.CNAME
    %import common.SIGNED_NUMBER
    %import common.WS
    
    %ignore WS
    %ignore COMMENT
    %ignore NEWLINE
"""


@v_args(inline=True)
class LibertyTransformer(Transformer):

    def escaped_string(self, s):
        return EscapedString(s[1:-1].replace('\\"', '"'))

    def string(self, s):
        return s[:]

    def name(self, s):
        return s[:]

    def number(self, s):
        return float(s)

    unit = string
    value = string

    def number_with_unit(self, num, unit):
        return WithUnit(num, unit)

    def simple_attribute(self, name, value):
        return {name: value}

    def complex_attribute(self, name, *values):
        return {name: list(values)}

    # @v_args(inline=True)
    # def value(self, value):
    #     return value
    def group_args(self, *args):
        return list(args)

    def group(self, group_name, group_args, *attributes):
        attrs = dict()
        sub_groups = []
        for a in attributes:
            if isinstance(a, dict):
                attrs.update(a)
            elif isinstance(a, Group):
                sub_groups.append(a)
            else:
                print(a)
                assert False

        return Group(group_name, group_args, attrs, sub_groups)


def parse_liberty(data: str) -> Group:
    """
    Parse a string containing data of a liberty file.
    :param data: Raw liberty string.
    :return: `Group` object of library.
    """
    liberty_parser = Lark(liberty_grammar,
                          parser='lalr',
                          lexer='standard',
                          transformer=LibertyTransformer())
    library = liberty_parser.parse(data)
    return library


def test_parse_liberty():
    import os.path
    lib_file = os.path.join(os.path.dirname(__file__), '../../test_data/gscl45nm.lib')

    data = open(lib_file).read()

    library = parse_liberty(data)

    library_str = str(library)
    open('/tmp/lib.lib', 'w').write(library_str)
    library2 = parse_liberty(library_str)

    cells = library.get_groups('cell')

    invx1 = library.get_group('cell', 'INVX1')
    assert invx1 is not None

    pin_y = invx1.get_group('pin', 'Y')
    timing_y = pin_y.get_group('timing')
    assert timing_y['related_pin'] == 'A'
    # print(pin_y)

    print(pin_y.get_group('timing').get_group('cell_rise').get_array('values'))
