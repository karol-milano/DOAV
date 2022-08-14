#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import sys
import json

import pandas as pd

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

work_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def jaccard_similarity(a, b):
    # calculate jaccard similarity
    return float(len(a.intersection(b))) / len(a.union(b))


def prepare_set():
    in_file = os.path.join(work_dir, "test_dataset.csv")

    projetos = []
    revisores = []
    authorship = []
    ownership = []

    print(in_file)
    with open(in_file, encoding="utf8", errors="ignore") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in tqdm(reader):
            if row["projeto"] not in projetos:
                projetos.append(row["projeto"])

            if row["ownership_arquivo"] == "1":
                ownership.append({
                    "projeto": row["projeto"],
                    "desenvolvedor": row["desenvolvedor"]
                })

            if row["doa_a"] != "" and float(row["doa_a"]) > 3.293 and float(row["doa_n"]) > 0.75:
                authorship.append({
                    "projeto": row["projeto"],
                    "desenvolvedor": row["desenvolvedor"]
                })

            revisores.append({
                "projeto": row["projeto"],
                "desenvolvedor": row["reviewer"]
            })

        out_file = os.path.join(work_dir, "ownership_set.csv")
        with open(out_file, "w", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames = ["projeto", "desenvolvedor"])
            writer.writeheader()

        out_file = os.path.join(work_dir, "authorship_set.csv")
        with open(out_file, "w", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames = ["projeto", "desenvolvedor"])
            writer.writeheader()

        out_file = os.path.join(work_dir, "revisores_set.csv")
        with open(out_file, "w", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames = ["projeto", "desenvolvedor"])
            writer.writeheader()

        revisores_dict = dict()
        authorship_dict = dict()
        ownership_dict = dict()
        for projeto in sorted(projetos):
            revisores_set = {x["desenvolvedor"] for x in revisores if x["projeto"] == projeto}
            authorship_set = {x["desenvolvedor"] for x in authorship if x["projeto"] == projeto}
            ownership_set = {x["desenvolvedor"] for x in ownership if x["projeto"] == projeto}

            revisores_dict[projeto] = revisores_set
            authorship_dict[projeto] = authorship_set
            ownership_dict[projeto] = ownership_set

            if len(ownership_set) > 0:
                out_file = os.path.join(work_dir, "ownership_set.csv")
                with open(out_file, "a", encoding="utf-8") as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames = ["projeto", "desenvolvedor"])
                    for x in ownership_set:
                        writer.writerow({
                            "projeto": projeto,
                            "desenvolvedor": x
                        })

            if len(authorship_set) > 0:
                out_file = os.path.join(work_dir, "authorship_set.csv")
                with open(out_file, "a", encoding="utf-8") as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames = ["projeto", "desenvolvedor"])
                    for x in authorship_set:
                        writer.writerow({
                            "projeto": projeto,
                            "desenvolvedor": x
                        })

            if len(revisores_set) > 0:
                out_file = os.path.join(work_dir, "revisores_set.csv")
                with open(out_file, "a", encoding="utf-8") as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames = ["projeto", "desenvolvedor"])
                    for x in revisores_set:
                        writer.writerow({
                            "projeto": projeto,
                            "desenvolvedor": x
                        })

    return projetos, revisores_dict, authorship_dict, ownership_dict


def jaccard(corte, projetos, revisores_dict, authorship_dict, ownership_dict):
    jac_dir = os.path.join(work_dir, "jaccard")
    corte_dir = os.path.join(jac_dir, "corte_" + str(corte))

    if not os.path.exists(corte_dir):
        os.makedirs(corte_dir)

    files = [f for f in sorted(os.listdir(jac_dir)) if len(f.split(".")) == 2 and f.split(".")[1] == "csv"]

    for jac_file in files:
        if not jac_file.startswith("formula"):
            continue

        input_file = os.path.join(jac_dir, jac_file)
        print(input_file)

        jac = []
        formula = []
        data = pd.read_csv(input_file)        
        for index, row in data.iterrows():
            if float(row['formula_valor']) > corte:
                formula.append({
                    "projeto": row["projeto"],
                    "desenvolvedor": row["desenvolvedor"]
                })

        out_file = os.path.join(corte_dir, "devs_" + jac_file)
        # out_file = os.path.join(work_dir, "jaccard_res.csv")
        with open(out_file, "w", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames = ["projeto", "desenvolvedor"])
            writer.writeheader()

        ###############################################################################

        for projeto in sorted(projetos):
            revisores_set = revisores_dict[projeto]
            authorship_set = authorship_dict[projeto]
            ownership_set = ownership_dict[projeto]

            formula_set = {x["desenvolvedor"] for x in formula if x["projeto"] == projeto}

            if len(formula_set) > 0:
                with open(out_file, "a", encoding="utf-8") as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames = ["projeto", "desenvolvedor"])
                    for x in formula_set:
                        writer.writerow({
                            "projeto": projeto,
                            "desenvolvedor": x
                        })

            ra = jaccard_similarity(revisores_set, authorship_set)
            ro = jaccard_similarity(revisores_set, ownership_set)
            rf = jaccard_similarity(revisores_set, formula_set)

            jac.append({
                "projeto": projeto,
                "authorship_similarity": round(ra, 5),
                "authorship_distance": round(1 - ra, 5),
                "ownership_similarity": round(ro, 5),
                "ownership_distance": round(1 - ro, 5),
                "formula_similarity": round(rf, 5),
                "formula_distance": round(1 - rf, 5),
                "nota_corte": corte
            })

        out_file = os.path.join(corte_dir, "jaccard_" + jac_file.split("formula_")[1])
        # out_file = os.path.join(work_dir, "jaccard_res.csv")
        with open(out_file, "w", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames = jac[0].keys())
            writer.writeheader()
            writer.writerows(jac)


if __name__ == "__main__":
    cortes = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.5, 0.75]

    projetos, revisores_dict, authorship_dict, ownership_dict = prepare_set()
    for corte in cortes:
        print(corte)
        jaccard(corte, projetos, revisores_dict, authorship_dict, ownership_dict)
