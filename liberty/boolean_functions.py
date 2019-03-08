##
## Copyright (c) 2019 Thomas Kramer.
## 
## This file is part of liberty-parser 
## (see https://codeberg.org/tok/liberty-parser).
## 
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program. If not, see <http://www.gnu.org/licenses/>.
##
import numpy as np
from typing import List
from lark import Lark, Transformer, v_args
import sympy
from functools import reduce

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
