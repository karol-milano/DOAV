#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import csv
import json
import math
import time
import locale

from author import *
from commit import *
from variability import *

from dateutil.parser import *

from datetime import datetime, timezone

is_ln = True
toCsv = True

locale.setlocale(locale.LC_ALL, '')
working_directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def save_file(out, rows, mode):
    print("Saving file " + out + " ... ")

    start_time = time.time()
    with open(out, mode) as outfile:
        dict_writer = csv.DictWriter(outfile, rows[0].keys())
        if mode != "a+":
            dict_writer.writeheader()
        
        dict_writer.writerows(rows)
        
    print("Saved in %s seconds" % (time.time() - start_time))


def parse_author_from_file(my_file, data):
    
    print("Parsing authors from file " + my_file + " ... ")
    start_time = time.time()
    rows_author = parse_author(data)        
    print("Parsed in %s seconds" % (time.time() - start_time))

    return rows_author


def parse_commit_from_file(my_file, data, rows_author):

    print("Parsing commits from file " + my_file + " ... ")
    start_time = time.time()
    rows_commit = parse_commit(rows_author, data)
    print("Parsed in %s seconds" % (time.time() - start_time))

    return rows_commit


def parse_variability_from_file(my_file, data):

    print("Parsing variabilities from file " + my_file + " ... ")
    start_time = time.time()
    rows_variability = parse_variability(data)
    print("Parsed in %s seconds" % (time.time() - start_time))

    return rows_variability


def main():
    
    for root, dirs, files in os.walk(working_directory + '/parsed_repositories'):
        for f in sorted(files):
            if '.json' in f:
                try:
                    with open(working_directory + '/parsed_repositories/' + f) as jfile:

                        my_file = f.split('.')[0]
                        print("Loading file " + my_file + " ... ", end='')
                        data = json.load(jfile)[my_file]
                        print("[OK]")

                        rows_author = parse_author_from_file(my_file, data)
                        rows_commit = parse_commit_from_file(my_file, data, rows_author)
                        rows_variability = parse_variability_from_file(my_file, data)

                        newpath = working_directory + '/graphs/' + my_file;
                        if not os.path.exists(newpath):
                            os.makedirs(newpath)

                        out = newpath + '/' + my_file + '_Authors.csv'
                        save_file(out, rows_author, 'w+')

                        out = newpath + '/' + my_file + '_Commits.csv'
                        save_file(out, rows_commit, 'w+')

                        if is_ln:
                            for r in rows_variability:
                                r['qtd_commits_geral'] = round(math.log(1 + r['qtd_commits_geral']), 3)
                                r['qtd_commits_dl'] = round(math.log(1 + r['qtd_commits_dl']), 3)
                                r['qtd_commits_ac'] = round(math.log(1 + r['qtd_commits_ac']), 3)

                        out = newpath + '/' + my_file + '_Variabilities.csv'
                        save_file(out, rows_variability, 'w+')

                        print()
                except ValueError as error:
                    print("[FAIL]")
                    print("Invalid json: %s" % error)
                    print()

if __name__ == "__main__":
    main()
