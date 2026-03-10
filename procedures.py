#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function

import json
import os
import sys

import xml.etree.ElementTree as ET


digits = [str(i) for i in sys.version_info]
print("Python {}".format(".".join(digits)))

file_args = {}
if sys.version_info.major >= 3:
    from json import JSONDecodeError
    file_args = {'encoding': "utf-8"}
else:
    JSONDecodeError = ValueError


def echo0(*args, **kwargs):
    kwargs['file'] = sys.stderr
    print(*args, **kwargs)


def check_json_files(root_dir):
    """Recursively finds all .json files and attempts to parse them."""
    ok = True
    print("Scanning for JSON files in: {}".format(root_dir))

    for root, _, files in os.walk(root_dir):
        # Skip hidden directories like .git
        if "/." in root or "\\." in root:
            continue

        for file in files:
            if not file.lower().endswith(".json"):
                continue
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, root_dir)

            try:
                with open(file_path, 'r', **file_args) as f:
                    json.load(f)
                print("✅ VALID: {}".format(relative_path))
            except (JSONDecodeError, UnicodeDecodeError) as e:
                echo0("❌ INVALID: {}".format(relative_path))
                echo0("   Error: {}".format(e))
                ok = False
            except Exception as e:
                echo0("❌ ERROR reading {}: {}".format(relative_path, e))
                ok = False

    return ok


def check_xml_files(root_dir):
    """Validates all .xml files recursively using built-in ElementTree."""
    print("Scanning for XML files in: {}".format(root_dir))
    ok = True
    for root, _, files in os.walk(root_dir):
        if ".git" in root.split(os.sep): continue
        for file in files:
            if not file.lower().endswith(".xml"):
                continue
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, root_dir)
            try:
                ET.parse(file_path)
                print("✅ XML  VALID: {}".format(rel_path))
            except ET.ParseError as e:
                print("❌ XML  INVALID: {}\n   Error: {}".format(rel_path, e))
                ok = False
            except Exception as e:
                print("❌ XML  ERROR: {}\n   Error: {}".format(rel_path, e))
                ok = False
    return ok


if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.abspath(__file__))

    code = 0
    if not check_json_files(root_dir):
        code += 1
        print("\nJSON validation failed.")
    else:
        print("\nAll JSON files are valid.")
    print("\n")
    if not check_xml_files(root_dir):
        code += 2
        print("\nXML validation failed.")
    else:
        print("\nAll XML files are valid.")

    sys.exit(code)
