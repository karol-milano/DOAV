#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import sys
import json
import operator

import pandas as pd

from tqdm import tqdm


maxInt = sys.maxsize
work_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

while True:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)


def insertIntoDict (dic, key, val = 1):
    """
    """
    if key in dic:
        dic[key] += val
    else:
        dic[key] = val


def unify_dataset():
    """
    """

    
    doa_dir = os.path.join(work_dir, "doa")
    data_dir = os.path.join(work_dir, "json")

    repos_file = os.path.join(work_dir, "repo.json")
    out_file = os.path.join(work_dir, "dataset.csv")

    repos = []
    ready = True

    print("Checking files...")
    with open(repos_file) as json_file:
        data = json.load(json_file)

    for repo in sorted(data, key=lambda x : x['repo'].lower()):
        r = repo["repo"].lower()
        repos.append(r)

        if not os.path.exists(os.path.join(doa_dir, r + "_commits.csv")):
            print("File not found: ", os.path.join(doa_dir, r + "_commits.csv"))
            ready = False

        if not os.path.exists(os.path.join(doa_dir, r + "_authors.csv")):
            print("File not found: ", os.path.join(doa_dir, r + "_authors.csv"))
            ready = False

        if not os.path.exists(os.path.join(doa_dir, r + "_variabilities.csv")):
            print("File not found: ", os.path.join(doa_dir, r + "_variabilities.csv"))
            ready = False

        if not os.path.exists(os.path.join(data_dir, r + ".json")):
            print("File not found: ", os.path.join(data_dir, r + ".json"))
            ready = False

    if not ready:
        return -1

    print("Preparing dataset...")
    with open(out_file, "w", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames = [
            "projeto",
            "id_desenvolvedor",
            "desenvolvedor",
            "arquivo",
            "variabilidade",
            "ownership_arquivo",
            "doa_a",
            "doa_n",
            "qtd_commits_arquivo",
            "fa_variabilidade",
            "qtd_commits_variabilidade",
            "dl_variabilidade",
            "ac_variabilidade",
            "qtd_arquivos_variabilidade",
            "qtd_commits_arquivo_variabilidade",
            "fa_arquivo_variabilidade",
            "ownership_variabilidade",
            "qtd_commits_pull",
            "requested",
            "created_by",
            "merged_by",
            "closed_by",
            "reviews",
            "id_reviewer",
            "reviewer"
        ])

        writer.writeheader()

        i = 1
        for projeto in repos:
            try:
                print("="*150)
                print("%s -- %d de %d" % (projeto, i, len(repos)))
                i += 1

                dataset = []
                in_file = os.path.join(doa_dir, projeto + "_commits.csv")
                with open(in_file, encoding="utf8", errors="ignore") as csv_file:
                    reader = csv.DictReader(csv_file)
                    reader = sorted(reader, key=operator.itemgetter('desenvolvedor'))

                    for row in reader:
                        if row["qtd_variabilidades"] == "0":
                            continue

                        dataset.append({
                            "projeto": projeto,
                            "hash": row["commit"] + row["arquivo"].strip(),
                            "desenvolvedor": row["desenvolvedor"].strip(),
                            "qtd_variabilidades": row["qtd_variabilidades"],
                            "arquivo": row["arquivo"].strip(),
                            "variabilidade": row["variabilidades"].strip(),
                            "ownership_arquivo": 1 if row["classificacao_ownership_final"] == "Major" else 0,
                            "doa_a": 0,
                            "doa_n": 0,
                            "qtd_commits_arquivo": 0,
                            "fa_variabilidade": 0,
                            "qtd_commits_variabilidade": 0,
                            "dl_variabilidade": 0,
                            "ac_variabilidade": 0,
                            "qtd_arquivos_variabilidade": 0,
                            "qtd_commits_arquivo_variabilidade": 0,
                            "fa_arquivo_variabilidade": 0,
                            "ownership_variabilidade": 0
                        })

                in_file = os.path.join(doa_dir, projeto + "_authors.csv")
                with open(in_file, encoding="utf8", errors="ignore") as csv_file:
                    reader = csv.DictReader(csv_file)
                    reader = sorted(reader, key=operator.itemgetter('desenvolvedor'))

                    for dt in tqdm(dataset, desc="Authors"):
                        for row in reader:
                            if dt["desenvolvedor"] == row["desenvolvedor"].strip() and \
                                dt["arquivo"] == row["arquivo"].strip() and \
                                dt["variabilidade"] == row["variabilidades"].strip():

                                doa_a = 0.0
                                doa_n = 0.0
                                if row["doa_a"] != "":
                                    doa_a = row["doa_a"]
                                    doa_n = row["doa_n"]

                                dt["doa_a"] = round(float(doa_a), 5)
                                dt["doa_n"] = round(float(doa_n), 5)
                                dt["qtd_commits_arquivo"] = row["qtd_commits"]

                                break

                        csv_file.seek(0)

                    print()

                in_file = os.path.join(doa_dir, projeto + "_variabilities.csv")
                with open(in_file, encoding="utf8", errors="ignore") as csv_file:
                    reader = csv.DictReader(csv_file)
                    reader = sorted(reader, key=operator.itemgetter('desenvolvedor'))

                    for dt in tqdm(dataset, desc="Variabilities"):
                        for row in reader:
                            if dt["desenvolvedor"] == row["desenvolvedor"] and \
                                dt["arquivo"] == row["arquivo"] and \
                                dt["variabilidade"] == row["variabilidade"]:

                                dt["fa_variabilidade"] = row["fa_geral"]
                                dt["qtd_commits_variabilidade"] = row["qtd_commits_geral"]
                                dt["dl_variabilidade"] = row["qtd_commits_dl"]
                                dt["ac_variabilidade"] = row["qtd_commits_ac"]
                                dt["qtd_arquivos_variabilidade"] = row["qtd_arquivos"]
                                dt["qtd_commits_arquivo_variabilidade"] = row["qtd_commits_arquivo"]
                                dt["fa_arquivo_variabilidade"] = row["fa_arquivo"]
                                dt["ownership_variabilidade"] = 1 if float(row["ownership_geral"]) > 5 else 0

                                break

                        csv_file.seek(0)

                user_set = {}
                for dt in dataset:
                    if dt["desenvolvedor"] not in user_set:
                        user_set[dt["desenvolvedor"]] = {}

                    if dt["hash"] not in user_set[dt["desenvolvedor"]]:
                        user_set[dt["desenvolvedor"]][dt["hash"]] = dt["qtd_variabilidades"]

                user_list = {}
                for dev, value in user_set.items():
                    if dev not in user_list:
                        user_list[dev] = 0

                    for qtd in value:
                        user_list[dev] += int(value[qtd])

                in_file = os.path.join(data_dir, projeto + ".json")
                with open(in_file, encoding="utf8", errors="ignore") as json_file:
                    data = json.load(json_file)

                for pull in data:
                    if len(pull["reviews"]) > 0:
                        for r in pull["reviews"]:
                            if r["user"] not in user_list:
                                user_list[r["user"]] = 0

                user_list = sorted(user_list.items(), key=operator.itemgetter(1), reverse=True)
                user_list = [k for k, v in user_list]

                pulls = {}
                for pull in data:
                    reviews = {}
                    if len(pull["reviews"]) > 0:
                        for r in pull["reviews"]:
                            if r["user"] in reviews:
                                reviews[r["user"]]["reviews"] += 1
                            else:
                                reviews[r["user"]] = {
                                    "id": user_list.index(r["user"]) + 1,
                                    "reviews": 1
                                }

                    if len(pull["commits"]) > 0:
                        for commit in pull["commits"]:

                            if commit["author"] not in pulls:
                                pulls[commit["author"]] = {
                                    "pulls": 1,
                                    "created_by": { pull["created_by"]: 1 },
                                    "closed_by": { pull["closed_by"]: 1 },
                                    "merged_by": { pull["merged_by"]: 1 },
                                    "requested": 1 if commit["author"] in pull["requested_reviewers"] else 0,
                                    "reviews": reviews
                                }
                            else:
                                requested = 1 if commit["author"] in pull["requested_reviewers"] else 0
                                pulls[commit["author"]]["pulls"] += 1

                                insertIntoDict(pulls[commit["author"]]["created_by"], pull["created_by"])
                                insertIntoDict(pulls[commit["author"]]["closed_by"], pull["closed_by"])
                                insertIntoDict(pulls[commit["author"]]["merged_by"], pull["merged_by"])
                                pulls[commit["author"]]["requested"] += requested
                                pulls[commit["author"]]["reviews"] = reviews

                final_data = []
                for d in dataset:
                    d.pop("qtd_variabilidades")
                    d.pop("hash")


                    if d["desenvolvedor"] in pulls:
                        created_by = 0
                        if d["desenvolvedor"] in pulls[d["desenvolvedor"]]["created_by"]:
                            created_by = pulls[d["desenvolvedor"]]["created_by"][d["desenvolvedor"]]

                        closed_by = 0
                        if d["desenvolvedor"] in pulls[d["desenvolvedor"]]["closed_by"]:
                            closed_by = pulls[d["desenvolvedor"]]["closed_by"][d["desenvolvedor"]]

                        merged_by = 0
                        if d["desenvolvedor"] in pulls[d["desenvolvedor"]]["merged_by"]:
                            merged_by = pulls[d["desenvolvedor"]]["merged_by"][d["desenvolvedor"]]

                        reviews = 0
                        if d["desenvolvedor"] in pulls[d["desenvolvedor"]]["reviews"]:
                            reviews = pulls[d["desenvolvedor"]]["reviews"][d["desenvolvedor"]]["reviews"]

                        d["qtd_commits_pull"] = pulls[d["desenvolvedor"]]["pulls"]
                        d["created_by"] = created_by
                        d["closed_by"] = closed_by
                        d["merged_by"] = merged_by
                        d["requested"] = pulls[d["desenvolvedor"]]["requested"]
                        d["reviews"] = reviews
                        d["reviewer"] = ""
                        d["id_reviewer"] = 0
                        d["id_desenvolvedor"] = user_list.index(d["desenvolvedor"]) + 1

                        if len(pulls[d["desenvolvedor"]]["reviews"]) > 0:
                            for reviewer in pulls[d["desenvolvedor"]]["reviews"]:
                                d["reviewer"] = reviewer
                                d["id_reviewer"] = pulls[d["desenvolvedor"]]["reviews"][reviewer]["id"]
                                final_data.append(d)
                        else:
                            final_data.append(d)
                    else:
                        d["qtd_commits_pull"] = 0
                        d["created_by"] = 0
                        d["closed_by"] = 0
                        d["merged_by"] = 0
                        d["requested"] = 0
                        d["reviews"] = 0
                        d["reviewer"] = ""
                        d["id_reviewer"] = 0
                        d["id_desenvolvedor"] = user_list.index(d["desenvolvedor"]) + 1

                        final_data.append(d)

                writer.writerows(final_data)
                print("[DONE]")
                

            except Exception as error:
                import traceback, sys
                exc = sys.exc_info()[0]
                stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
                if exc is not None:  # i.e. an exception is present
                    del stack[-1]       # remove call of full_stack, the printed exception
                                        # will contain the caught exception caller instead
                trc = "Traceback (most recent call last):\n"
                stackstr = trc + "".join(traceback.format_list(stack))
                if exc is not None:
                    stackstr += "  " + traceback.format_exc().lstrip(trc)
                print(stackstr)


def split_train_test():

    in_file = os.path.join(work_dir, "dataset.csv")
    train_dataset_file = os.path.join(work_dir, "train_dataset.csv")
    test_dataset_file = os.path.join(work_dir, "test_dataset.csv")

    data = pd.read_csv(in_file)

    columns = [
        "qtd_commits_variabilidade",
        "dl_variabilidade",
        "ac_variabilidade",
        "qtd_arquivos_variabilidade",
        "qtd_commits_arquivo_variabilidade",
        "ownership_variabilidade",
        "qtd_commits_pull",
        "requested",
        "reviews",
        "created_by",
        "merged_by",
        "closed_by"
    ]

    for col in columns:
        groups = data.groupby('projeto')[col]
        maxes = groups.transform('max')
        mins = groups.transform('min')
        data = data.assign(col=(data[col] - mins)/(maxes - mins))

    train_dataset = []
    test_dataset = []
    for name, group in data.groupby("projeto"):
        if group["id_reviewer"].sum() > 700:
            test_dataset.append(group)
        else:
            train_dataset.append(group)

    print("Saving file... %s" % (test_dataset_file))
    pd.concat(test_dataset).to_csv(test_dataset_file, index = False)
    print("[DONE]")
    
    print("Saving file... %s" % (train_dataset_file))
    pd.concat(train_dataset).to_csv(train_dataset_file, index = False)
    print("[DONE]")

if __name__ == "__main__":
    unify_dataset()
    split_train_test()
