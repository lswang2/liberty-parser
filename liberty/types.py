from typing import Any, List, Dict, Optional
from itertools import chain
from .util import strings_to_array, array_to_strings, parse_boolean_function
import numpy as np


class Group:
    def __init__(self, group_name: str,
                 args: List[str] = None,
                 attributes: Dict[str, Any] = None,
                 groups: List = None):
        self.group_name = group_name
        self.args = args if args is not None else []
        self.attributes = attributes if attributes is not None else dict()
        self.groups = groups if groups is not None else []

    def get_groups(self, type_name: str, argument: Optional[str] = None) -> List:
        """ Get all groups of type `type_name`.
        Optionally filter the groups by their first argument.
        :param type_name:
        :param argument:
        :return: List[Group]
        """
        return [g for g in self.groups
                if g.group_name == type_name
                and (argument is None or
                     (len(g.args) > 0 and g.args[0] == argument)
                     )
                ]

    def get_group(self, type_name: str, argument: Optional[str] = None):
        """
        Get exactly one group of type `type_name`.
        :param type_name:
        :return: Group
        """
        groups = self.get_groups(type_name, argument=argument)
        assert len(groups) == 1, "There must be exactly one instance of group '{}'.".format(type_name)
        return groups[0]

    def __repr__(self) -> str:
        return "%s (%s) t{%s, %s}" % (self.group_name, self.args, self.attributes, self.groups)

    def __str__(self) -> str:
        """
        Create formatted string representation that can be dumped to a liberty file.
        :return:
        """
        return "\n".join(self._format())

    def _format(self, indent: str = " " * 2) -> List[str]:
        """
        Create the liberty file format line by line.
        :return: A list of lines.
        """

        def format_value(v) -> str:
            return str(v)

        sub_group_lines = [g._format(indent=indent) for g in self.groups]
        attr_lines = list()
        for k, v in sorted(self.attributes.items()):
            if isinstance(v, list):
                # Complex attribute
                formatted = [format_value(x) for x in v]

                if any((isinstance(x, EscapedString) for x in v)):
                    attr_lines.append('{} ('.format(k))
                    for i, l in enumerate(formatted):
                        if i < len(formatted) - 1:
                            end = ', \\'
                        else:
                            end = ''
                        attr_lines.append(indent + l + end)
                    attr_lines.append(');')
                else:
                    values = "({})".format(", ".join(formatted))
                    attr_lines.append("{} {};".format(k, values))
            else:
                # Simple attribute
                values = format_value(v)
                attr_lines.append("{}: {};".format(k, values))

        lines = list()
        lines.append("{} ({}) {{".format(self.group_name, ", ".join(self.args)))
        for l in chain(attr_lines, *sub_group_lines):
            lines.append(indent + l)

        lines.append("}")

        return lines

    def __getitem__(self, item):
        return self.attributes[item]

    def __setitem__(self, key, value):
        self.attributes[key] = value

    def __contains__(self, item):
        return item in self.attributes

    def get(self, key, default=None):
        return self.attributes.get(key, default)

    def get_array(self, key) -> np.ndarray:
        """
        Get a 1D or 2D array as a numpy.ndarray object.
        :param key: Name of the attribute.
        :return: ndarray
        """
        str_array = self[key]
        str_array = [s.value for s in str_array]
        return strings_to_array(str_array)

    def set_array(self, key, value: np.ndarray):
        str_array = array_to_strings(value)
        str_array = [EscapedString(s) for s in str_array]
        self[key] = str_array

    def get_boolean_function(self, key):
        """
        Get parsed boolean expression.
        Intended for getting the value of the `function` attribute of pins.
        :param key:
        :return:
        """
        f_str = self[key]
        f = parse_boolean_function(f_str)
        return f


class CellGroup(Group):

    def __init__(self, cell_name: str, attributes: Dict[str, Any],
                 sub_groups: List[Group]):
        super().__init__("cell", args=[cell_name], attributes=attributes,
                         groups=sub_groups)
        self.name = cell_name


class WithUnit:
    """
    Store a value with a unit attached.
    """

    def __init__(self, value, unit: str):
        self.value = value
        self.unit = unit

    def __str__(self):
        return "{}{}".format(self.value, self.unit)

    def __repr__(self):
        return str(self)


class EscapedString:

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return '"{}"'.format(self.value)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, EscapedString):
            return self.value == other.value
        else:
            return self.value == other


def select_cell(library: Group, cell_name: str) -> Optional[Group]:
    """
    Select a cell by name from a library group.
    :param library:
    :param cell_name:
    :return:
    """
    available_cell_names = {g.args[0] for g in library.get_groups('cell')}

    if cell_name in available_cell_names:
        return library.get_group('cell', cell_name)
    else:
        raise Exception("Cell name must be one of: {}".format(list(sorted(available_cell_names))))


def select_pin(cell: Group, pin_name: str) -> Optional[Group]:
    """
    Select a pin by name from a cell group.
    :param cell:
    :param pin_name:
    :return:
    """
    available_pin_names = {g.args[0] for g in cell.get_groups('pin')}

    if pin_name in available_pin_names:
        return cell.get_group('pin', pin_name)
    else:
        raise Exception("Pin name must be one of: {}".format(list(sorted(available_pin_names))))


def select_timing_table(pin: Group, related_pin: str, table_name: str) -> Optional[Group]:
    """
    Select a timing table by name from a pin group.
    :param pin:
    :param related_pin:
    :param table_name:
    :return:
    """
    timing_group_by_related_pin = {g['related_pin'].value: g for g in pin.get_groups('timing')
                                   if 'related_pin' in g}
    if related_pin not in timing_group_by_related_pin:
        raise Exception(("Related pin name must be one of: {}".
                         format(list(sorted(timing_group_by_related_pin.keys())))))

    timing_group = timing_group_by_related_pin[related_pin]
    available_table_names = {g.group_name for g in timing_group.groups}

    if table_name in available_table_names:
        return timing_group.get_group(table_name)
    else:
        raise Exception(("Table name must be one of: {}".format(list(sorted(available_table_names)))))
