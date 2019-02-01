#!/usr/bin/env python3

"""
Copyright 2019 Kamil Rusin

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import argparse
import hashlib
import json
import os
import signal
import sys
import time
import xlrd

class Generator(object):
  def __init__(self, path, output, metadata_path, simple):
    self.path = path
    self.output = output
    self.filename = os.path.splitext(os.path.basename(self.path))[0]
    self.indent_level = 0
    self.metadata_path = metadata_path
    self.simple = simple

    self.load_metadata()


  def load_metadata(self):
    if self.metadata_path is None:
      self.meta_name = "PROJECT_NAME"
      self.meta_detail = "PROJECT_DETAIL"
    else:
      with open(self.metadata_path, "rb") as f:
        data = json.load(f)
      self.meta_name = data["name"]
      self.meta_detail = data["short_description"]


  def get_hash(self):
    hash_utl = hashlib.md5()
    with open(self.path, "rb") as f:
      for chunk in iter(lambda: f.read(4096), b""):
        hash_utl.update(chunk)
    return hash_utl.hexdigest()


  def watch(self, interval):
    self.file_hash = self.get_hash()
    print("Watching for file changes...")
    while True:
      time.sleep(inverval)
      new_hash = self.get_hash()
      if self.file_hash != new_hash:
        print("The file has been changed.")
        self.file_hash = new_hash
        self.read_and_generate()


  def find_multiple_defs(self):
    key_to_defs = dict()
    for sheet_name, sheet in self.sheets.items():
      for idx, row in enumerate(sheet):
        phrase = row[0].lower()
        if phrase in key_to_defs.keys():
          key_to_defs[phrase].append((sheet_name, idx))
        else:
          key_to_defs[phrase] = [(sheet_name, idx)]

      for key, defs_idxs in key_to_defs.items():
        if len(defs_idxs) > 1:
          print(f"\nWARNING: Multiple definitions of '{key}':", file=sys.stderr)
          for sheet_name, idx in defs_idxs:
            print(f"\t[{sheet_name}]: {self.sheets[sheet_name][idx][1]}", file=sys.stderr)
          print("\n")


  def merge_sheets(self):
    self.merged_sheets = []
    for _, rows in self.sheets.items():
      self.merged_sheets.extend(rows)


  def read_and_generate(self):
    data_xls = xlrd.open_workbook(self.path)
    self.sheets = dict()
    for sheet_name in data_xls.sheet_names():
      self.sheets[sheet_name] = []
      sheet = data_xls.sheet_by_name(sheet_name)
      for row in sheet.get_rows():  # returns a generator
        tmp = [cell.value for cell in row]
        if tmp[0] == '':  # if there's not phrase
          continue
        self.sheets[sheet_name].append(list(filter(None, tmp)))
      if not self.simple:
        self.generate_tsv(sheet_name, self.sheets[sheet_name])
        self.generate_xml(sheet_name, self.sheets[sheet_name])

    self.find_multiple_defs()
    self.merge_sheets()
    self.generate_tsv(self.filename, self.merged_sheets)
    self.generate_xml(self.filename, self.merged_sheets)


  def generate_tsv(self, name, rows):
    tsv_file = os.path.join(self.output, name) + ".tsv"
    print(f"Generating the '{tsv_file}' TSV file.")
    with open(tsv_file, "wb") as f:
      for row in rows:
        f.write(str.encode("\t".join(row) + os.linesep))


  def generate_xml(self, name, rows):
    xml_file = os.path.join(self.output, name) + ".xml"
    print(f"Generating the '{xml_file}' XML file.")
    with open(xml_file, "wb") as f:
      f.write(self.format('<?xml version="1.0" encoding="UTF-8"?>'))
      f.write(self.format('<GLOSSARY>'))
      f.write(self.format('<INFO>', '>'))
      f.write(self.format(f'<NAME>{self.meta_name}</NAME>', '>'))
      f.write(self.format(f'<INTRO>{self.meta_detail}</INTRO>'))
      f.write(self.format('<INTROFORMAT>1</INTROFORMAT>'))
      f.write(self.format('<ALLOWDUPLICATEDENTRIES>0</ALLOWDUPLICATEDENTRIES>'))
      f.write(self.format('<DISPLAYFORMAT>dictionary</DISPLAYFORMAT>'))
      f.write(self.format('<SHOWSPECIAL>1</SHOWSPECIAL>'))
      f.write(self.format('<SHOWALPHABET>1</SHOWALPHABET>'))
      f.write(self.format('<SHOWALL>1</SHOWALL>'))
      f.write(self.format('<ALLOWCOMMENTS>0</ALLOWCOMMENTS>'))
      f.write(self.format('<USEDYNALINK>1</USEDYNALINK>'))
      f.write(self.format('<ALLOWCOMMENTS>0</ALLOWCOMMENTS>'))
      f.write(self.format('<DEFAULTAPPROVAL>1</DEFAULTAPPROVAL>'))
      f.write(self.format('<GLOBALGLOSSARY>0</GLOBALGLOSSARY>'))
      f.write(self.format('<ENTBYPAGE>10</ENTBYPAGE>'))
      f.write(self.format('<ENTRIES>'))

      for idx, row in enumerate(rows):
        if idx == 0:
          f.write(self.format('<ENTRY>', '>'))
        else:
          f.write(self.format('<ENTRY>'))
        f.write(self.format(f'<CONCEPT>{row[0]}</CONCEPT>', '>'))
        f.write(self.format(f'<DEFINITION>{row[1]}</DEFINITION>'))
        f.write(self.format('<FORMAT>0</FORMAT>'))
        f.write(self.format('<USEDYNALINK>0</USEDYNALINK>'))
        f.write(self.format('<CASESENSITIVE>0</CASESENSITIVE>'))
        f.write(self.format('<FULLMATCH>0</FULLMATCH>'))
        f.write(self.format('<TEACHERENTRY>1</TEACHERENTRY>'))
        if len(row) > 2:
          f.write(self.format('<ALIASES>'))
          for alias in row[2:]:
            f.write(self.format('<ALIAS>', '>'))
            f.write(self.format(f'<NAME>{alias}</NAME>', '>'))
            f.write(self.format('</ALIAS>', '<'))
          f.write(self.format('</ALIASES>', '<'))
        f.write(self.format('</ENTRY>', '<'))

      f.write(self.format('</ENTRIES>', '<'))
      f.write(self.format('</INFO>', '<'))
      f.write(self.format('</GLOSSARY>', '<'))

    if self.metadata_path is None:
      print("\n===================================")
      print("Don't forget to change the metadata in the generated xml file!")
      print("===================================\n")


  def format(self, line, indent_direction = "="):
    if indent_direction == ">":
      self.indent_level += 1
    elif indent_direction == "<":
      self.indent_level -= 1
    return str.encode(self.get_indent() + line + os.linesep)


  def get_indent(self, tabs_to_spaces = True):
    if tabs_to_spaces:
      return "  " * self.indent_level
    return "\t" * self.indent_level


def reciveSignal(signalNumber, frame):
  sys.exit("\n\nInterupted. Exiting gracefully.")


def main():
  signal.signal(signal.SIGTERM, reciveSignal)
  signal.signal(signal.SIGINT, reciveSignal)
  signal.signal(signal.SIGQUIT, reciveSignal)

  parser = argparse.ArgumentParser()
  parser.add_argument("path", metavar="PATH", help="path to a XLSX file")
  parser.add_argument("-o", "--output-dir",
      help="output directory path (default: CWD)", default=".")
  parser.add_argument("-w", "--watch", type=float, default=-1.0, nargs="?",
      metavar="INTERVAL", help="watch for file changes (default interval: .5s)")
  parser.add_argument("-m", "--metadata", type=str, metavar="META_FILE_PATH",
      help="metadata JSON file path")
  parser.add_argument("-s", "--simple", action="store_true", default=False,
      help="if given, the script will not generate files for each sheet")
  args = parser.parse_args()

  if not os.path.isdir(args.output_dir):
    if os.path.exists(args.output_dir):
      print("The given output path exists, but is not a directory.",
          file=sys.stderr)
      print("Setting CWD as the output directory.")
      args.output_dir = "."
    else:
      os.makedirs(args.output_dir)

  g = Generator(args.path, args.output_dir, args.metadata, args.simple)
  if args.watch != -1.0:
    g.watch(0.5 if args.watch == None else args.watch)
  else:
    g.read_and_generate()


if __name__ == "__main__":
  main()
