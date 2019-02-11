import numpy as np
from typing import List


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
