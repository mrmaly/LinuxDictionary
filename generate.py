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
import os
import signal
import sys
import time
import xlrd

class Generator(object):
  def __init__(self, path, output):
    self.path = path
    self.output = output
    if not os.path.isdir(self.output):
      if os.path.exists(self.output):
        print("The given output path exists, but is not a directory.",
            file=sys.stderr)
        print("Setting CWD as the output directory.")
        self.output = "."
      else:
        os.makedirs(self.output)
    self.filename = os.path.splitext(os.path.basename(self.path))[0]
    self.indent_level = 0

  def get_hash(self):
    hash_utl = hashlib.md5()
    with open(self.path, "rb") as f:
      for chunk in iter(lambda: f.read(4096), b""):
        hash_utl.update(chunk)
    return hash_utl.hexdigest()

  def watch(self):
    self.file_hash = self.get_hash()
    print("Watching for file changes...")
    while True:
      time.sleep(.5)
      new_hash = self.get_hash()
      if self.file_hash != new_hash:
        print("The file has been changed.")
        self.file_hash = new_hash
        self.read_and_generate()


  def read_and_generate(self):
    data_xls = xlrd.open_workbook(self.path)
    print(f"Reading the first sheet from '{self.path}' file.")
    sheet = data_xls.sheet_by_index(0)
    self.rows = []
    for row in sheet.get_rows():  # returns a generator
      tmp = [cell.value for cell in row]
      if tmp[0] == '':  # if there's not phrase
        continue
      self.rows.append(list(filter(None, tmp)))  # removes empty cells

    self.generate_tsv()
    self.generate_xml()


  def generate_tsv(self):
    tsv_file = os.path.join(self.output, self.filename) + ".tsv"
    print(f"Generating the '{tsv_file}' TSV file.")

    print(f"File '{tsv_file}' has been generated.")


  def generate_xml(self):
    xml_file = os.path.join(self.output, self.filename) + ".xml"
    print(f"Generating the '{xml_file}' XML file.")
    with open(xml_file, "wb") as f:
      f.write(self.format('<?xml version="1.0" encoding="UTF-8"?>'))
      f.write(self.format('<GLOSSARY>'))
      f.write(self.format('<INFO>', '>'))
      f.write(self.format('<NAME>PROJECT_NAME</NAME>', '>'))
      f.write(self.format('<INTRO>PROJECT DESCRIPTION</INTRO>'))
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

      for idx, row in enumerate(self.rows):
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

    print(f"File '{xml_file}' has been generated.")
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
  parser.add_argument("path", help="path to a XLSX file")
  parser.add_argument("-o", "--output-dir",
      help="output directory path (default: CWD)", default=".")
  parser.add_argument("-w", "--watch", help="watch for file changes",
      action="store_true")
  args = parser.parse_args()

  g = Generator(args.path, args.output_dir)
  if args.watch:
    g.watch()
  else:
    g.read_and_generate()


if __name__ == "__main__":
  main()
