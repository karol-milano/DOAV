#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import json
import unidecode

from file import *
from author import *
from commit import *
from variability import *

from tqdm import tqdm
from pydriller import Repository
from datetime import datetime, timezone


working_directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_dir = os.path.join(working_directory, "data")
cloned_repos = os.path.join(data_dir, "cloned_repositories")
extract_variables_directory = os.path.join(data_dir, "extracted_variables")
repos_file = os.path.join(working_directory, "repos.json")

allowed_extensions = [".c", ".cpp", ".h", ".hpp"]

field_names = [
    "Author", "Date", "File", "Adds", "Dels", "Mods", "Amount", "FA", "Blame",
    "NumCommits", "NumDays", "NumModDevs", "Size", "AvgDaysCommits"
]

def extract_variables():

    # clona até essa data
    date_to = datetime(2023, 11, 10, 22, 00, 00, tzinfo=timezone.utc)

    with open(repos_file) as json_file:
        json_data = json.load(json_file)

    for row in json_data:
        project = row['repo'].lower()
        url = os.path.join(cloned_repos, project)

        filename = os.path.join(extract_variables_directory, project + ".csv")
        with open(filename, 'w+') as csv_file:
            dict_writer = csv.DictWriter(csv_file, field_names)
            dict_writer.writeheader()
            
            autores = dict()
            print("Cloning repository [%s]..." % project, end='')
            t_commits = Repository(url, to=date_to, clone_repo_to=cloned_repos).traverse_commits()
            print("[DONE]")

            for commit in tqdm(t_commits, "Traversing repository [%s]" % project):
                try:
                    name = unidecode.unidecode(commit.author.name.title().strip())
                    
                    for modified_file in commit.modified_files:
                        filename, ext = os.path.splitext(modified_file.filename)
                        if ext not in allowed_extensions:
                            continue

                        delta = date_to - commit.author_date

                        dict_writer.writerow({
                            "Author": name,
                            "Date": commit.author_date,
                            "File": modified_file.filename.lower(),
                            "Adds": modified_file.added_lines,
                            "Dels": modified_file.deleted_lines,
                            "Mods": 0,
                            "Amount": modified_file.added_lines + modified_file.deleted_lines,
                            "FA": 1 if modified_file.old_path is None else 0,
                            "Blame": 0,
                            "NumCommits": 1,
                            "NumDays": delta.days,
                            "NumModDevs": 0,
                            "Size": modified_file.nloc,
                            "AvgDaysCommits": 0
                        })

                except:
                    print("Exception")
                    print(commit.hash)
                    print(commit.author_date)
                    print("="*150)
                    import traceback, sys
                    exc = sys.exc_info()[0]
                    stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
                    if exc is not None:  # i.e. an exception is present
                        del stack[-1]       # remove call of full_stack, the printed exception
                                            # will contain the caught exception caller instead
                    trc = 'Traceback (most recent call last):\n'
                    stackstr = trc + ''.join(traceback.format_list(stack))
                    if exc is not None:
                        stackstr += '  ' + traceback.format_exc().lstrip(trc)
                    print(stackstr)
        
        print("="*150)


if __name__ == '__main__':
    extract_variables()