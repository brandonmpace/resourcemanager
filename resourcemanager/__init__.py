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

"""Package for handling download/update/loading of resources (e.g. json files)"""

__author__ = "Brandon M. Pace"
__copyright__ = "Copyright 2019, Brandon M. Pace"
__license__ = "GNU LGPL 3+"
__maintainer__ = "Brandon M. Pace"
__status__ = "Development"
__version__ = "0.0.3"

import logging


from .handlers import read_file, save_file, read_json, save_json
from .manager import count_of_loaded_resources, count_of_total_resources, loaded_resource_percentage
from .manager import get_resource_instance, register_resource, set_max_workers
from .resourceclasses import FileResource, JsonResource


logger = logging.getLogger(__name__)
