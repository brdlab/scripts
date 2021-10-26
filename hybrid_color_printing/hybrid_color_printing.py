#!/usr/bin/env python3

# Simple script for finding and counting the color pages in a PDF
# Licensed under the GPLv3
#
# This script is based on the following threads:
#
#   http://tex.stackexchange.com/questions/53493
#   https://gist.github.com/bluezio/7625935
#
# Code has been tested for windows only. It can work on MacOS and
# Linux, please check the appropriate commands for running
# Ghostscript and edit line 41

import logging
import re
import subprocess
from os import path, access, R_OK

VERSION = "1.0.4"

RE_FLOAT = re.compile("[01].[0-9]+")
CMYK_NCOLORS = 4

logging.basicConfig(level=logging.ERROR)


def is_color(c, m, y, k):
  if c==m==y:
    return 0
  else:
    return 1

def cmyk_per_page(pdf_file):
  if not path.isfile(pdf_file):
    raise Exception("{} does not exist or is not a file".format(pdf_file))
  if not access(pdf_file, R_OK):
    raise Exception("{} is not readable".format(pdf_file))

  gs_inkcov = subprocess.Popen(
      ["gswin64c", "-o", "out.txt", "-sDEVICE=inkcov", pdf_file], stdout=subprocess.PIPE)

  with open('out.txt', 'r') as f:
    for line in f:
      fields = line.split()
      if (len(fields) >= CMYK_NCOLORS
          and all(RE_FLOAT.match(fields[i]) for i in range(CMYK_NCOLORS))):
        cmyk = tuple(float(value) for value in fields[0:CMYK_NCOLORS])
        logging.debug("Extracted fields %s", cmyk)
        yield cmyk
  f.close()


def count_page_types(pdf_file):
  nb, nc = 0, 0
  for page in cmyk_per_page(pdf_file):
    if is_color(*page):
      nc += 1
    else:
      nb += 1
  return (nb, nc)


def find_color_pages(pdf_file):
  for n, page in enumerate(cmyk_per_page(pdf_file), 1):
    if is_color(*page):
      logging.debug("Page", n, "is a color page")
      yield (n, page)

def find_bw_pages(pdf_file):
  for n, page in enumerate(cmyk_per_page(pdf_file), 1):
    if not is_color(*page):
      logging.debug("Page", n, "is a b/w page")
      yield (n, page)

def double_side(pagelist):
  printlist = []
  for i in range(len(pagelist)):
    if cpagelist[i] % 2 == 0:
      printlist.append(pagelist[i] - 1)
      printlist.append(pagelist[i])
    else:
      printlist.append(pagelist[i])
      printlist.append(pagelist[i] + 1)
  return list(set(printlist))

def complement(pagelist, n):
  printlist = []
  for i in range(n):
    if i+1 in pagelist:
      continue
    else:
      printlist.append(i+1)
  return list(set(printlist))

def ranges(printlist):
  printlist = sorted(set(printlist))
  gaps = [[s, e] for s, e in zip(printlist, printlist[1:]) if s+1 < e]
  edges = iter(printlist[:1] + sum(gaps, []) +printlist[-1:])
  rangelist = list(zip(edges, edges))
  stringlist = []
  for i in rangelist:
    if i[0] == i[1]:
      stringlist.append(str(i[0]))
      continue
    if i[0] + 1 == i[1]:
      stringlist.append(str(i[0]))
      stringlist.append(str(i[1]))
      continue
    else:
      stringlist.append(str(i[0])+'-'+str(i[1]))
      continue
  return ','.join(stringlist)

if __name__ == "__main__":
  import argparse

  parser = argparse.ArgumentParser(description="""Lists or counts the
    colour pages of a PDF file on standard output. The utility
    requires having the 'gs' tool from Ghostscript 9.5 or later
    installed and available through the PATH.""")

  parser.add_argument("file", help="PDF file to be analyzed")

  parser.add_argument("--count", "-c", action='store_true',
                      help="Print the number of pages instead of listing them")

  parser.add_argument("--debug", "-d", action='store_true',
                      help="Enables verbose debugging output")

  parser.add_argument("--noheader", "-H", action='store_true',
                      help="Disables the first header line")

  parser.add_argument("--doubleside", "-DS", action='store_true',
                      help="Outputs list of color and b/w pages for double sided printing")

  parser.add_argument("--fullstring", "-F", action='store_true',
                      help="""Enables output in range string format, 
                      to input in print dialogue boxes, e.g. 2-14, 19-32""")

  parser.add_argument("--costb", "-B", metavar="PB", type=float,
                      help="B/W page price (for total cost report, " +
                           "requires --pcolor as well)")

  parser.add_argument("--costc", "-C", metavar="PB", type=float,
                      help="B/W page price (for total cost report, " +
                           "requires --pcolor as well)")

  args = parser.parse_args()

  if args.debug:
    logging.getLogger('').setLevel(logging.DEBUG)
  if args.costc is not None and args.costb is None:
    raise Exception(
      "Page price was specified for color but not for B/W pages")
  if args.costb is not None and args.costc is None:
    raise Exception(
      "Page price was specified for B/W but not for color pages")

  if args.count:
    print('Number of colored pages is:', count_page_types(args.file)[1])

  elif args.costc is not None and args.costb is not None:
    nb, nc = count_page_types(args.file)
    total_cost = args.costb * nb + args.costc * nc
    print(("Total cost ({0:d} B/W @ {1:3.6g}/page "
           + "and {2:d} color @ {3:3.6g}/page): {4:3.6g}")
          .format(nb, args.costb, nc, args.costc, total_cost))
  else:
    if not args.noheader:
      logging.debug("\t".join(("n", "c", "m", "y", "k")))
    cpagelist = []
    bwpagelist = []
    for n, cmyk in find_color_pages(args.file):
      cpagelist.append(n)
      logging.debug("\t".join((str(s) for s in (n,) + cmyk)))

    for n, cmyk in find_bw_pages(args.file):
      bwpagelist.append(n)
      logging.debug("\t".join((str(s) for s in (n,) + cmyk)))

    print("Number of colored pages are:", len(cpagelist))
    print("Number of b/w pages are:", len(bwpagelist))
    totalpages = len(cpagelist) + len(bwpagelist)

    if not args.doubleside:
      if not args.fullstring:
        print("Color pages are:", ranges(cpagelist))
        print("B/W pages are:", ranges(bwpagelist))
      else:
        print("Color pages are:", ','.join(str(i) for i in cpagelist))
        print("B/W pages are:", ','.join(str(i) for i in bwpagelist))

    else:
      cprintlist = double_side(cpagelist)
      bwprintlist = complement(cpagelist, totalpages)
      if not args.fullstring:
        print("Color pages are:", ranges(cprintlist))
        print("B/W pages are:", ranges(bwprintlist))
      else:
        print("Color pages are:", ','.join(str(i) for i in cprintlist))
        print("B/W pages are:", ','.join(str(i) for i in bwprintlist))