#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import sys
import locale

csv.field_size_limit(sys.maxsize)

locale.setlocale(locale.LC_ALL, '')
working_directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def split_commits (commits):
    ids = []
    commits = commits.split(", ")
    for commit in commits:
        id_commit = commit.split("  -  ")[0]
        id_commit = id_commit.strip()
        ids.append(id_commit)

    return " - ".join(ids)


def rq3_doa():

    total = []
    os.chdir(working_directory)

    for root in sorted(os.listdir("graphs/")):
        colaboradores = dict()
        autores = dict()
        
        devs = []
        variabilities = []
        with open("graphs/" + root + "/" + root + "_authors.csv") as csvfile:
            reader = csv.DictReader(csvfile)

            commits = ""
            for r in reader:
                if r["commits"] != "" and commits != r["commits"]:
                    commits = r["commits"]

                if r["autor"] == "Colaborador" and r["variabilidades"] != "":
                    if r["variabilidades"] not in colaboradores:
                        colaboradores[r["variabilidades"]] = []

                    colaboradores[r["variabilidades"]].append({
                        "arquivo": r["arquivo"],
                        "commits": split_commits(commits),
                        "variabilidades": r["variabilidades"],
                        "desenvolvedor": r["desenvolvedor"],
                        "autor": r["autor"]
                    })
                elif r["autor"] == "Autor" and r["variabilidades"] == "":
                    if r["arquivo"] not in autores:
                        autores[r["arquivo"]] = []

                    autores[r["arquivo"]].append({
                        "arquivo": r["arquivo"],
                        "commits": split_commits(commits),
                        "variabilidades": r["variabilidades"],
                        "desenvolvedor": r["desenvolvedor"],
                        "autor": r["autor"]
                    })
            
            csvfile.seek(0)

            for r in reader:
                if r["desenvolvedor"] not in devs:
                    devs.append(r["desenvolvedor"])

                if r["variabilidades"] != "":

                    if r["variabilidades"] not in variabilities:
                        variabilities.append(r["variabilidades"])

                    if r["autor"] == "Autor":
                        if r["variabilidades"] in colaboradores:
                            colaboradores.pop(r["variabilidades"])

                        if r["arquivo"] in autores:
                            autores.pop(r["arquivo"])

        authors_n = [] # Authors that never touched variability
        variabilities_n = [] # Variabilities never touched by authors
        print("Saving file: graphs/" + root + "/rq3_doa.csv ... ")
        with open("graphs/" + root + "/rq3_doa.csv", "w+") as outfile:
            dict_writer = csv.DictWriter(outfile, ["arquivo", "commits", "variabilidades", "desenvolvedor", "autor"])
            dict_writer.writeheader()

            for colab in colaboradores.values():
                dict_writer.writerows(colab)
                for r in colab:
                    if r["variabilidades"] not in variabilities_n:
                        variabilities_n.append(r["variabilidades"])

            for aut in autores.values():
                dict_writer.writerows(aut)
                for r in aut:
                    if r["desenvolvedor"] not in authors_n:
                        authors_n.append(r["desenvolvedor"])

        total.append({
            "Projeto": root,
            "Autores": len(authors_n),
            "Developers_n": len(devs),
            "Colaboradores": len(variabilities_n),
            "Variabilities_n": len(variabilities)
        })

    with open("rq3_doa_total.csv", "w+") as outfile:
        dict_writer = csv.DictWriter(outfile, ["Projeto", "Autores", "Developers_n", "Colaboradores", "Variabilities_n"])
        dict_writer.writeheader()
        dict_writer.writerows(total)


def rq3_ownership():

    total = []
    os.chdir(working_directory)

    for root in sorted(os.listdir("graphs/")):
        minors = dict()
        majors = dict()
        
        devs = []
        variabilities = []
        with open("graphs/" + root + "/" + root + "_commits.csv") as csvfile:
            reader = csv.DictReader(csvfile)

            for r in reader:
                if r["classificacao_ownership_final"] == "Minor" and r["variabilidades"] != "":
                    if r["variabilidades"] not in minors:
                        minors[r["variabilidades"]] = []

                    minors[r["variabilidades"]].append({
                        "arquivo": r["arquivo"],
                        "commit": r["commit"],
                        "variabilidades": r["variabilidades"],
                        "desenvolvedor": r["desenvolvedor"],
                        "classificacao_ownership_final": r["classificacao_ownership_final"]
                    })
                elif r["classificacao_ownership_final"] == "Major" and r["variabilidades"] == "":
                    if r["arquivo"] not in majors:
                        majors[r["arquivo"]] = []

                    majors[r["arquivo"]].append({
                        "arquivo": r["arquivo"],
                        "commit": r["commit"],
                        "variabilidades": r["variabilidades"],
                        "desenvolvedor": r["desenvolvedor"],
                        "classificacao_ownership_final": r["classificacao_ownership_final"]
                    })
            
            csvfile.seek(0)

            for r in reader:
                if r["desenvolvedor"] not in devs:
                    devs.append(r["desenvolvedor"])

                if r["variabilidades"] != "":
                    if r["variabilidades"] not in variabilities:
                        variabilities.append(r["variabilidades"])

                    if r["classificacao_ownership_final"] == "Major":
                        if r["variabilidades"] in minors:
                            minors.pop(r["variabilidades"])

                        if r["arquivo"] in majors:
                            majors.pop(r["arquivo"])

        majors_n = [] # Majors that never touched variability
        variabilities_n = [] # Variabilities never touched by majors
        print("Saving file: graphs/" + root + "/rq3_ownership.csv ... ")
        with open("graphs/" + root + "/rq3_ownership.csv", "w+") as outfile:
            dict_writer = csv.DictWriter(outfile, ["arquivo", "commit", "variabilidades", "desenvolvedor", "classificacao_ownership_final"])
            dict_writer.writeheader()

            for min in minors.values():
                dict_writer.writerows(min)
                for r in min:
                    if r["variabilidades"] not in variabilities_n:
                        variabilities_n.append(r["variabilidades"])
            
            for maj in majors.values():
                dict_writer.writerows(maj)
                for r in maj:
                    if r["desenvolvedor"] not in majors_n:
                        majors_n.append(r["desenvolvedor"])

        total.append({
            "Projeto": root,
            "Majors": len(majors_n),
            "Developers_n": len(devs),
            "Minors": len(variabilities_n),
            "Variabilities_n": len(variabilities)
        })

    with open("rq3_ownership_total.csv", "w+") as outfile:
        dict_writer = csv.DictWriter(outfile, ["Projeto", "Majors", "Developers_n", "Minors", "Variabilities_n"])
        dict_writer.writeheader()
        dict_writer.writerows(total)

if __name__ == "__main__":
    rq3_doa()
    rq3_ownership()
