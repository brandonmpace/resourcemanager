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

"""Module for classes that represent and handle resources"""

import datetime
import logging
import os
import threading


from typing import Callable, Optional, Union
from .constants import DATE_FORMAT, NOT_UPDATED
from .handlers import save_file, read_json, save_json, validate_json


logger = logging.getLogger(__name__)


class FileResource(object):
    """Object that represents a loadable resource"""
    def __init__(
            self,
            name: str,
            file_path: str,
            loader: Callable,
            reader: Callable = None,
            writer: Callable = None,
            updater: Callable = None,
            validator: Callable = None,
            binary: bool = False
    ):
        """
        Initialize a FileResource instance
        Note: reader and updater should produce the same return value (e.g. str or bytes)

        :param name: str name identifier for this resource
        :param file_path: str path to file
        :param loader: Callable that accepts file path (or data when reader is provided) and loads data for your program
        :param reader: Callable that accepts file path and returns data that will be passed to loader function
        :param writer: Callable that accepts file path and data to save to disk, then returns True on success
        :param updater: Callable that fetches data to save for the resource (e.g. returns file content from a web API)
        :param validator: Callable that accepts file path (or data when reader is provided) and returns True when valid
        """
        self.name = name
        self.file_path = file_path
        self.loader: Callable = loader
        self.reader: Optional[Callable] = reader
        self.writer: Optional[Callable] = writer
        self.updater: Optional[Callable] = updater
        self.validator: Optional[Callable] = validator
        self.binary: bool = binary

        self.last_update: datetime.datetime = NOT_UPDATED
        self.loaded = False
        self.updated = False
        self._lock = threading.RLock()

    def can_read(self) -> bool:
        return self.reader is not None

    def can_save(self) -> bool:
        return self.writer is not None

    def can_update(self) -> bool:
        return self.updater is not None

    def can_validate(self) -> bool:
        return self.validator is not None

    def exists(self) -> bool:
        return os.path.isfile(self.file_path)

    def load(self):
        with self._lock:
            error_message = f"Unable to load resource '{self.name}' from '{self.file_path}'"
            if self.exists() or self.update():
                if self.reader:
                    data = self.reader(self.file_path)
                    if self.validate(data=data):
                        self.loader(data)
                        self.loaded = True
                    elif (self.last_update is NOT_UPDATED) and self.update():
                        data = self.reader(self.file_path)
                        if self.validate(data=data):
                            self.loader(data)
                            self.loaded = True
                        else:
                            raise ValueError(error_message)
                    else:
                        raise ValueError(error_message)
                else:
                    if self.validate():
                        self.loader(self.file_path)
                        self.loaded = True
                    elif (self.last_update is NOT_UPDATED) and self.update():
                        if self.validate():
                            self.loader(self.file_path)
                            self.loaded = True
                        else:
                            raise ValueError(error_message)
                    else:
                        raise ValueError(error_message)
            else:
                raise FileNotFoundError(error_message)

    def save(self, data):
        with self._lock:
            if self.reader and (self.validate(data=data) is False):
                return False
            if self.writer:
                return self.writer(self.file_path, data)
            else:
                return save_file(self.file_path, data, binary=self.binary)

    def set_last_update(self, last_update: Union[datetime.datetime, str]):
        if isinstance(last_update, str):
            try:
                self.last_update = datetime.datetime.strptime(last_update, DATE_FORMAT)
            except ValueError:
                logger.error(f"Received date string with unexpected format: '{last_update}'")
        elif isinstance(last_update, datetime.datetime):
            self.last_update = last_update
        else:
            raise ValueError(f"Invalid type for last_update: {type(last_update)}")

    def update(self) -> bool:
        with self._lock:
            if self.updater:
                data = self.updater()
                if self.save(data):
                    self.set_last_update(datetime.datetime.utcnow())
                    self.updated = True
                    return True
            return False

    def validate(self, data=None) -> bool:
        if self.validator:
            if self.reader:
                if data is None:
                    return_value = self.validator(self.reader(self.file_path))
                else:
                    return_value = self.validator(data)
            else:
                return_value = self.validator(self.file_path)
            if return_value is False:
                logger.error(f"resource '{self.name}' from '{self.file_path}' failed validation")
            return return_value
        else:
            # without a validator we have no way to say the data is bad, so we return True
            return True


class JsonResource(FileResource):
    """Object that represents a loadable resource"""
    def __init__(
            self,
            name: str,
            file_path: str,
            loader: Callable,
            reader: Callable = read_json,
            writer: Callable = save_json,
            updater: Callable = None,
            validator: Callable = validate_json
    ):
        """
        Initialize a JsonResource instance
        Note: reader and updater should produce the same return value (dictionary that represents valid JSON)

        :param name: str name identifier for this resource
        :param file_path: str path to file
        :param loader: Callable that accepts keyword args that are keys from your JSON (**kwargs is also recommended)
        :param reader: Callable that accepts file path and returns a dict representing JSON
        :param writer: Callable that accepts file path and JSON dict to save to disk, then returns True on success
        :param updater: Callable that fetches an updated dict representing JSON to save to disk, last_update datetime is passed to it
        :param validator: Callable that accepts a dict representing JSON and returns True when valid

        :todo: Handle differential updates, where server only sends content created since last_update timestamp
        """
        if not (reader and writer and validator):
            raise ValueError("JsonResource requires a valid reader, writer and validator")
        super().__init__(
            name,
            file_path,
            loader,
            reader=reader,
            writer=writer,
            updater=updater,
            validator=validator,
            binary=False
        )

    def load(self):
        with self._lock:
            error_message = f"Unable to load resource '{self.name}' from '{self.file_path}'"
            if self.exists() or self.update():
                data = self.reader(self.file_path)
                if self.validate(data=data):
                    if "last_update" in data:
                        self.set_last_update(data["last_update"])
                    self.loader(**data)
                    self.loaded = True
                elif self.update():
                    data = self.reader(self.file_path)
                    if self.validate(data=data):
                        self.loader(**data)
                        self.loaded = True
                    else:
                        raise ValueError(error_message)
                else:
                    raise ValueError(error_message)
            else:
                raise FileNotFoundError(error_message)

    def validate(self, data: dict = None) -> bool:
        if data is None:
            return_value = self.validator(self.reader(self.file_path))
        else:
            return_value = self.validator(data)
        if return_value is False:
            logger.error(f"resource '{self.name}' from '{self.file_path}' failed validation")
        return return_value

    def update(self) -> bool:
        with self._lock:
            if self.updater:
                data = self.updater(self.last_update)
                if self.save(data):
                    if "last_update" in data:
                        self.set_last_update(data["last_update"])
                    else:
                        self.set_last_update(datetime.datetime.utcnow())
                    self.updated = True
                    return True
            return False
