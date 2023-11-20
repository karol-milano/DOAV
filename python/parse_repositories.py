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
from datetime import datetime
from pydriller import Repository
from preprocessor import Preprocessor


working_directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_dir = os.path.join(working_directory, "data")
cloned_repos = os.path.join(data_dir, "cloned_repositories")
repositories = os.path.join(data_dir, "repositories")
parsed_repositories = os.path.join(data_dir, "parsed_repositories")
repos_file = os.path.join(working_directory, "repos.json")

allowed_extensions = [".c", ".cpp", ".h", ".hpp"]
reserved_names = ["con", "prn", "aux", "nul", "com0", "com1", "com2", "com3", "com4", "com5", "com6", "com7", "com8", "com9", "lpt0", "lpt1", "lpt2", "lpt3", "lpt4", "lpt5", "lpt6", "lpt7", "lpt8", "lpt9"]

def clone_repositories(json_data):

    # clona até essa data
    date_to = datetime(2023, 11, 10, 22, 00, 00)

    for row in json_data:
        project = row['repo'].lower()
        clone = int(row['clone'])

        if clone == 0:
            continue

        url = "https://github.com/{}/{}".format(row['owner'], project)
        repo_dir = os.path.join(repositories, project)

        if clone == 2: # local repository
            url = os.path.join(cloned_repos, project)

        print("Preparing to clone %s/%s..." % (row['owner'], project))            

        with open(repo_dir + ".csv", 'w') as csv_file:
            dict_writer = csv.DictWriter(csv_file, ["Commit", "Author", "Date", "FileCount"])
            dict_writer.writeheader()
            
            autores = dict()
            print("Cloning repository [%s]..." % project, end='')
            t_commits = Repository(url, to=date_to, clone_repo_to=cloned_repos).traverse_commits()
            print("[DONE]")

            for commit in tqdm(t_commits, "Traversing repository [%s]" % project):
                try:
                    email = commit.author.email.lower().strip()
                    name = unidecode.unidecode(commit.author.name.title().strip())

                    if email not in autores:
                        autores[email] = name
                    else:
                        name = autores[email]

                    path = os.path.join(repo_dir, commit.hash)

                    file_count = 0
                    for modified_file in commit.modified_files:
                        filename, ext = os.path.splitext(modified_file.filename)
                        if ext not in allowed_extensions:
                            continue

                        aux = ""
                        file_count += 1
                        if modified_file.new_path is not None: # Arquivo não existia
                            aux = modified_file.new_path.split("/")
                        elif modified_file.old_path is not None: # Arquivo foi removido
                            aux = modified_file.old_path.split("/")

                        modified = os.path.join(path, "/".join(aux[1:-1]))
                        if not os.path.exists(modified):
                            os.makedirs(modified)

                        if filename.lower() in reserved_names:
                            filename += "_"

                        modified = os.path.join(modified, filename + ext)

                        with open(modified, 'w') as f:
                            f.write(modified_file.diff)

                    dict_writer.writerow({
                        "Commit": commit.hash,
                        "Author": name,
                        "Date": commit.author_date,
                        "FileCount": file_count
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


def parse_files(json_data):
    repos = [f["repo"].lower() for f in json_data if f["parse"] == 1]

    for repo in sorted(repos):
        if os.path.exists(os.path.join(repositories, repo + ".csv")):
            parse_repo(repo)


def parse_repo(project = "Cherokee"):
    repositories_project_dir = os.path.join(repositories, project)
    parsed_project_dir = os.path.join(parsed_repositories, project)

    if not os.path.exists(parsed_project_dir):
        os.makedirs(parsed_project_dir)

    arquivos = {}
    autores = {}
    commits = {}
    variabilidades = {}

    with open(repositories_project_dir + ".csv") as csv_file:
        csv_file.seek(0, 0)

        csv_reader = csv.DictReader(csv_file)

        output_var_csv = os.path.join(parsed_repositories, project + ".csv")
        with open(output_var_csv, "w+") as output_csv:
            header = [
                "Commit",
                "Data",
                "Autor",
                "Email",
                "Arquivo",
                "Mudanca por arquivo",
                "Variabilidade",
                "Mudanca por variabilidade"
            ]

            dict_writer = csv.DictWriter(output_csv, header)
            dict_writer.writeheader()

            for row in tqdm(csv_reader, "Parsing repository [%s]" % project):
                if int(row['FileCount']) > 0:

                    id_commit = row['Commit'].strip()
                    author_name = row['Author'].strip()
                    author_email = ""
                    date = row['Date'].strip()

                    input_path = os.path.join(repositories_project_dir, id_commit)
                    output_path = os.path.join(parsed_project_dir, id_commit)

                    for root, dirs, files in os.walk(input_path):
                        for file_name in sorted(files):
                            ext = os.path.splitext(file_name)[-1]
                            if ext not in allowed_extensions:
                                continue

                            root_dir = os.path.join(input_path, root)
                            input_file = os.path.join(root_dir, file_name)
                            
                            tmp = root_dir.split(id_commit)
                            output = output_path + tmp[1]

                            if not os.path.exists(output):
                                os.makedirs(output)

                            output_file = os.path.join(output, file_name + ".var")

                            rd = root.split(id_commit + "/")
                            if len(rd) > 1:
                                file_name = os.path.join(rd[1], file_name)
                            
                            var_list, buffer = Preprocessor().parse_save(input_file, output_file, id_commit, date, author_name, author_email, file_name)

                            dict_writer.writerows(buffer)
                            
                            #################################################################################
                            ############## Arquivos
                            #################################################################################
                            if file_name in arquivos:
                                arquivos[file_name] = update_arquivo(arquivos[file_name], id_commit, author_name, author_email, file_name, date, var_list)
                            else:
                                arquivos[file_name] = create_arquivo(id_commit, author_name, author_email, file_name, date, var_list)


                            #################################################################################
                            ############## Autores
                            #################################################################################
                            if author_name in autores:
                                autores[author_name] = update_author(autores[author_name], id_commit, author_name, author_email, file_name, date, var_list)
                            else:
                                autores[author_name] = create_author(id_commit, author_name, author_email, file_name, date, var_list)


                            #################################################################################
                            ############## Commits
                            #################################################################################
                            if id_commit in commits:
                                commits[id_commit] = update_commit(commits[id_commit], id_commit, author_name, author_email, file_name, date, var_list)
                            else:
                                commits[id_commit] = create_commit(id_commit, author_name, author_email, file_name, date, var_list)


                            #################################################################################
                            ############## Variabilidades
                            #################################################################################
                            for var in var_list:
                                if var in variabilidades:
                                    variabilidades[var] = update_variability(variabilidades[var], id_commit, author_name, author_email, file_name, date, var)
                                else:
                                    variabilidades[var] = create_variability(id_commit, author_name, author_email, file_name, date, var)

    #################################################################################################
    #### Salva o JSON no arquivo
    #################################################################################################

    data = {}
    data[project] = {}
    data[project]["Arquivos"] = arquivos
    data[project]["Autores"] = autores
    data[project]["Commits"] = commits
    data[project]["Variabilidades"] = variabilidades

    output_json = os.path.join(parsed_repositories, project + ".json")
    with open(output_json, "w+") as json_file:
        json.dump(data, json_file, indent = 4, sort_keys = True)


if __name__ == "__main__":
    if not os.path.exists(cloned_repos):
        os.makedirs(cloned_repos)

    if not os.path.exists(repositories):
        os.makedirs(repositories)

    if not os.path.exists(parsed_repositories):
        os.makedirs(parsed_repositories)

    with open(repos_file) as json_file:
        json_data = json.load(json_file)

    clone_repositories(json_data)
    parse_files(json_data)
