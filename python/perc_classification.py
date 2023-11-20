#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import sys
import locale
import operator


csv.field_size_limit(sys.maxsize)

locale.setlocale(locale.LC_ALL, '')
working_directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
graphs_directory = os.path.join(working_directory, "data", "graphs")


def calculate_percentage():

    dados = []

    for root in sorted(os.listdir(graphs_directory)):

        authors = {}
        with open(os.path.join(graphs_directory, root , root + "_authors.csv")) as csvfile:
            reader = csv.DictReader(csvfile)
            reader = sorted(reader, key=operator.itemgetter('desenvolvedor'))

            for row in reader:
                if row["classificacao"] != "":
                    if row["desenvolvedor"] not in authors:
                        authors[row["desenvolvedor"]] = row["classificacao"]
                    elif authors[row["desenvolvedor"]] != row["classificacao"]:
                        authors[row["desenvolvedor"]] = "Misto"

        counter = {"Especialista": 0, "Generalista": 0, "Misto": 0}
        for k, v in authors.items():
            counter[v] += 1

        dados.append({
            "repo": root,
            "devs": len(authors),
            "Especialista": counter["Especialista"],
            "Generalista": counter["Generalista"],
            "Misto": counter["Misto"],
            "Perc_Especialista": round(counter["Especialista"] / len(authors) * 100, 3),
            "Perc_Generalista": round(counter["Generalista"] / len(authors) * 100, 3),
            "Perc_Misto": round(counter["Misto"] / len(authors) * 100, 3)
        })

    with open(os.path.join(working_directory, "data", "perc_classification.csv"), "w+") as outfile:
        dict_writer = csv.DictWriter(outfile, dados[0].keys())
        dict_writer.writeheader()
        dict_writer.writerows(dados)


if __name__ == '__main__':
    calculate_percentage()