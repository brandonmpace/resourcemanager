#!/usr/bin/env python3

import datetime
import functools
import resourcemanager
import time


example_global = ""
example_json_item = ""


def fetch_file():
    return "Example file content\nFor testing."


def fetch_json(last_update: datetime.datetime = None):
    # Example: If last_update is provided, use `datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f")`
    # then send that string to the server in a POST, which allows it to send only content updated after that
    # It is planned to have JsonResource be able to handle the merging for such cases in the future.
    test_data = {"last_update": "2019-09-23T05:01:55.783131", "key": "value", "other": "other_value", "extra": 1}
    return test_data


def example_loader(input_data: str):
    global example_global
    print(f"example_loader: Got: '{input_data}'")
    example_global = input_data


def example_json_loader(key: str, other: str, **kwargs):
    global example_json_item
    print(f"example_json_loader: Got: key '{key}', other '{other}', kwargs '{kwargs}'")
    example_json_item = key


def example_validator(file_path: str) -> bool:
    with open(file_path) as file_handle:
        return file_handle.read().startswith("Example")


def example_text_validator(text_data: str) -> bool:
    return text_data.startswith("Example")


def example_json_validator(data: dict) -> bool:
    return ("key" in data) and ("other" in data)


example_resource = resourcemanager.FileResource(
    "example file", "example.txt", example_loader, updater=fetch_file, validator=example_validator
)

example_json_resource = resourcemanager.JsonResource(
    "example JSON file", "example.json", example_json_loader, updater=fetch_json, validator=example_json_validator
)

print(f"Example file exists: {example_resource.exists()}")
print(f"Example JSON file exists: {example_json_resource.exists()}")
resourcemanager.register_resource(example_resource)
resourcemanager.register_resource(example_json_resource)
print(f"{resourcemanager.loaded_resource_percentage()}% loaded")
time.sleep(0.05)
print(f"{resourcemanager.loaded_resource_percentage()}% loaded")

if example_resource.loaded:
    print(f"Example global after load: '{example_global}'")
else:
    print(f"resource still loading")
time.sleep(1)

print(f"Example JSON global after JSON load: '{example_json_item}'")


ascii_reader = functools.partial(resourcemanager.read_file, encoding='ascii', errors='replace')
example_resource = resourcemanager.FileResource(
    "example file", "example.txt", example_loader, reader=ascii_reader, updater=fetch_file, validator=example_text_validator
)
example_resource.load()
print(f"Example global after second load: '{example_global}'")
