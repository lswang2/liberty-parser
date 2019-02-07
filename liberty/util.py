import numpy as np
from typing import List
from lark import Lark, Transformer, v_args
import sympy
from functools import reduce


def array_to_strings(array: np.ndarray) -> List[str]:
    """
    Convert a numpy array into a liberty string format.
    :param array:
    :return:
    """
    array = array.astype(np.float)
    if array.ndim == 1:
        array = [array]
    return [
        ", ".join(("{0:f}".format(x) for x in row))
        for row in array
    ]


def strings_to_array(strings: List[str]) -> np.array:
    """
    Convert liberty string array format in to a numpy array.
    :param strings:
    :return:
    """
    array = [
        np.fromstring(s.replace("\\\n", ""), sep=',')
        for s in strings
    ]
    return np.array(array)


def test_array_to_strings():
    a = np.array([[1, 2, 3], [4, 5, 6]])
    s = array_to_strings(a)
    a2 = strings_to_array(s)

    assert (a == a2).all()


"""
Parsing boolean functions of liberty format

Operator precedence: First XOR, then AND then OR

Operator Description
’ Invert previous expression
! Invert following expression
^ Logical XOR
* Logical AND
& Logical AND
space Logical AND
+ Logical OR
| Logical OR
1 Signal tied to logic 1
0 Signal tied to logic 0
"""

boolean_function_grammar = r"""

    ?start: or_expr

    ?or_expr: and_expr ([ "+" | "|" ] and_expr)*

    ?and_expr: xor_expr ([ "&" | "*" ]? xor_expr)*

    ?xor_expr: atom
        | xor_expr "^" xor_expr

    ?atom: CNAME -> name
        | "!" atom -> not_expr
        | atom "'" -> not_expr
        | "(" or_expr ")"

    %import common.CNAME
    %import common.WS_INLINE

    %ignore WS_INLINE
"""


@v_args(inline=True)
class BooleanFunctionTransformer(Transformer):
    from operator import __inv__

    def or_expr(self, *exprs):
        from operator import __or__
        return reduce(__or__, exprs)

    def and_expr(self, *exprs):
        from operator import __and__
        return reduce(__and__, exprs)

    def xor_expr(self, *exprs):
        from operator import __xor__
        return reduce(__xor__, exprs)

    not_expr = __inv__

    def name(self, n):
        return sympy.Symbol(n)


def parse_boolean_function(data: str):
    """
    Parse a boolean function into a sympy formula.
    :param data: String representation of boolean expression as defined in liberty format.
    :return: sympy formula
    """
    liberty_parser = Lark(boolean_function_grammar,
                          parser='lalr',
                          lexer='standard',
                          transformer=BooleanFunctionTransformer()
                          )
    function = liberty_parser.parse(data)
    return function


def test_parse_boolean_function():
    f_str = "A' + B + C & D + E ^ F * G | (H + I)"
    f_actual = parse_boolean_function(f_str)
    a, b, c, d, e, f, g, h, i = sympy.symbols('A B C D E F G H I')

    f_exp = ~a | b | c & d | (e ^ f) & g | (h | i)

    assert f_actual == f_exp
