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

"""Module for the actual management of resources"""

import logging
import queue
import threading


from .resourceclasses import FileResource
from typing import Dict, Optional, Tuple


logger = logging.getLogger(__name__)


_manager_lock = threading.RLock()
_manager_thread: Optional[threading.Thread] = None
_manager_thread_count = 0
_pending_queue = queue.Queue()  # Queue of Optional[Tuple[FileResource, bool, bool]]
_queue_timeout = 1
_resources_lock = threading.RLock()
_resources: Dict[str, FileResource] = {}


def get_resource_instance(name: str) -> Optional[FileResource]:
    with _resources_lock:
        return _resources.get(name, None)


def register_resource(resource: FileResource, load_before_update: bool = True, update: bool = True):
    """
    Register a resource for automatic loading and updating.
    :param resource: FileResource or subclass (must have a unique name attribute)
    :param load_before_update: bool whether or not loading resource should be attempted before updating
    :param update: bool whether or not an explicit update should be attempted
    :return: None
    """
    with _resources_lock:
        if resource.name in _resources:
            raise ValueError(f"Resource already registered with name '{resource.name}'")
        else:
            _resources[resource.name] = resource
        _pending_queue.put((resource, load_before_update, update))
        _run_manager()


def count_of_loaded_resources() -> int:
    with _resources_lock:
        return len([_ for _ in _resources.values() if _.loaded])


def count_of_total_resources() -> int:
    with _resources_lock:
        return len(_resources)


def loaded_resource_percentage() -> float:
    with _resources_lock:
        total_resource_count = count_of_total_resources()
        loaded_resource_count = count_of_loaded_resources()
        if total_resource_count == 0:
            return 0.0
        else:
            return (loaded_resource_count / total_resource_count) * 100


def _handle_pending_queue():
    while True:
        try:
            pending_item: Optional[Tuple[FileResource, bool, bool]] = _pending_queue.get(
                block=True, timeout=_queue_timeout
            )
            if pending_item is None:
                break
            resource = pending_item[0]
            load_before_update = pending_item[1]
            update = pending_item[2]

            should_load_now = (update and load_before_update) or (update is False and load_before_update is False)
            if should_load_now:
                try:
                    resource.load()
                except Exception:
                    logger.exception(f"Failed to load resource '{resource.name}'")

            # update the resource if asked to and it wasn't updated during load()
            if update and (resource.updated is False):
                try:
                    resource.update()
                except Exception:
                    logger.exception(f"Failed to update resource '{resource.name}'")

        except queue.Empty:  # timeout reached
            if _pending_queue.empty():
                break

        except Exception:
            logger.exception("Encountered exception while handling pending queue")


def _run_manager():
    global _manager_thread
    global _manager_thread_count
    with _manager_lock:
        if _manager_thread and _manager_thread.is_alive():
            logger.debug("Not starting new manager thread as one exists and is alive")
        else:
            _manager_thread_count += 1
            _manager_thread = threading.Thread(
                target=_handle_pending_queue, name=f"res_mgr{_manager_thread_count}", daemon=True
            )
            _manager_thread.start()
