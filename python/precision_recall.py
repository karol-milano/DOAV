#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import sys
import json

from tqdm import tqdm


maxInt = sys.maxsize

while True:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)


working_directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
graphs = os.path.join(working_directory, "data", "graphs")
repos_file = os.path.join(working_directory, "repos.json")


if __name__ == "__main__":
    print("Loading repos...", end="")
    with open(repos_file) as json_file:
        repos = json.load(json_file)
    print("[OK]")
    print("="*80)

    data = []
    total_devs = total_doa = total_doa_geral = total_own = total_own_geral = total_var = 0
    for repo in sorted(repos, key=lambda x : x['repo'].lower()):
        r = repo["repo"].lower()

        devs = set()
        var_devs = set()
        doa_devs = set()
        doa_devs_geral = set()
        own_devs = set()
        own_devs_geral = set()
        
        authors_file = os.path.join(graphs, r, r + "_authors.csv")
        with open(authors_file, encoding="utf8", errors="ignore") as csv_file:
            reader = csv.DictReader(csv_file)

            for row in tqdm(reader, desc="Processing " + r + "_authors"):
                isDOA = False
                dev = row["desenvolvedor"].lower().strip()

                devs.add(dev)
                if row["doa_a"] != "" and float(row["doa_a"]) > 3.293 and float(row["doa_n"]) > 0.75:
                    doa_devs_geral.add(dev)
                    isDOA = True

                if row["qtd_variabilidades"] != "" and int(row["qtd_variabilidades"]) > 0:
                    var_devs.add(dev)
                    
                    if isDOA:
                        doa_devs.add(dev)

        commits_file = os.path.join(graphs, r, r + "_commits.csv")
        with open(commits_file, encoding="utf8", errors="ignore") as csv_file:
            reader = csv.DictReader(csv_file)
            
            for row in tqdm(reader, desc="Processing " + r + "_commits"):
                isOwnership = False
                dev = row["desenvolvedor"].lower().strip()

                devs.add(dev)
                if row["classificacao_ownership_final"] == "Major":
                    own_devs_geral.add(dev)
                    isOwnership = True

                if row["qtd_variabilidades"] != "" and int(row["qtd_variabilidades"]) > 0:
                    var_devs.add(dev)
                    
                    if isOwnership:
                        own_devs.add(dev)

        data.append({
            "project": r,
            "total_devs": len(devs),
            "variabilities_devs": len(var_devs),
            "doa_devs": len(doa_devs),
            "doa_devs_geral": len(doa_devs_geral),
            "doa_variabilities_recall": round(len(doa_devs) / len(var_devs), 3),
            "ownership_devs": len(own_devs),
            "ownership_devs_geral": len(own_devs_geral),
            "ownership_variabilities_recall": round(len(own_devs) / len(var_devs), 3),
        })

        total_devs += len(devs)
        total_doa += len(doa_devs)
        total_own += len(own_devs)
        total_var += len(var_devs)
        total_doa_geral += len(doa_devs_geral)
        total_own_geral += len(own_devs_geral)

        print("="*80)

    data.append({
        "project": "Total",
        "total_devs": total_devs,
        "variabilities_devs": total_var,
        "doa_devs": total_doa,
        "doa_devs_geral": total_doa_geral,
        "doa_variabilities_recall": round(total_doa / total_var, 3),
        "ownership_devs": total_own,
        "ownership_devs_geral": total_own_geral,
        "ownership_variabilities_recall": round(total_own / total_var, 3)
    })

    out_file = os.path.join(working_directory, "data", "precision_recall.csv")
    with open(out_file, "w", encoding="utf8", errors="ignore") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)