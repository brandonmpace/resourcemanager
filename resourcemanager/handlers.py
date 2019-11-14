# -*- coding: UTF-8 -*-
# Copyright (C) 2019 Brandon M. Pace
#
# This file is part of resourcemanager
#
# resourcemanager is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# resourcemanager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with resourcemanager.
# If not, see <https://www.gnu.org/licenses/>.

"""Module for file handlers (readers/writers)"""

import json

from typing import Dict, List, Union


def read_file(file_path: str, encoding: str = "UTF-8", errors: str = "strict", binary: bool = False) -> Union[bytes, str]:
    if binary:
        with open(file_path, mode="rb") as file_handle:
            return file_handle.read()
    else:
        with open(file_path, mode="r", encoding=encoding, errors=errors) as file_handle:
            return file_handle.read()


def save_file(file_path: str, data, encoding: str = "UTF-8", errors: str = "strict", binary: bool = False) -> bool:
    if binary:
        encoding = None
        errors = None
        mode_string = 'wb'
    else:
        mode_string = 'w'
    with open(file_path, mode=mode_string, encoding=encoding, errors=errors) as file_handle:
        file_handle.write(data)

    return True


def read_json(file_path: str, encoding: str = 'UTF-8') -> dict:
    with open(file_path, encoding=encoding) as file_handle:
        try:
            data = json.load(file_handle)
        except json.JSONDecodeError:
            return {}
        else:
            return data


def save_json(
        file_path: str,
        data: Dict[str, Union[Dict, float, int, List, str]],
        indent: int = 4,
        encoding: str = 'UTF-8'
) -> bool:
    with open(file_path, mode="w", encoding=encoding) as file_handle:
        json.dump(data, file_handle, indent=indent)

    return True


def validate_json(**kwargs) -> bool:
    try:
        json.dumps(kwargs)
    except TypeError:
        return False
    else:
        return True
