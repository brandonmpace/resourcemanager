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

"""Module for static variables"""

import datetime

# format of the recommended datetime.datetime.utcnow().isoformat()
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

# default last_update for a resource
NOT_UPDATED = datetime.datetime(1970, 1, 1)
