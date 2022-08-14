#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import sys

import pandas as pd

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
data_dir = os.path.join(working_directory, "data")


def doav(a, b, c, d, e):
    return 1.44601 + a * 0.36413 + b * -0.00732 + c * -0.32662 + d * 0.63357 + e * -0.00439

def calculate_doav():
    test_dataset = os.path.join(data_dir, "test_dataset.csv")

    with open(test_dataset) as csv_file:
        reader = csv.DictReader(csv_file)

        data = []
        for row in reader:
            fa_variabilidade = 0
            qtd_arquivos_variabilidade = 0
            qtd_commits_arquivo_variabilidade = 0
            dl_variabilidade = 0
            ac_variabilidade = 0

            try:
                fa_variabilidade = float(row["fa_variabilidade"])
            except:
                pass

            try:
                qtd_arquivos_variabilidade = float(row["qtd_arquivos_variabilidade"])
            except:
                pass

            try:
                qtd_commits_arquivo_variabilidade = float(row["qtd_commits_arquivo_variabilidade"])
            except:
                pass

            try:
                dl_variabilidade = float(row["dl_variabilidade"])
            except:
                pass

            try:
                ac_variabilidade = float(row["ac_variabilidade"])
            except:
                pass

            res = doav(
                fa_variabilidade,
                qtd_commits_arquivo_variabilidade,
                dl_variabilidade,
                ac_variabilidade,
                qtd_arquivos_variabilidade
            )

            data.append({
                "projeto": row["projeto"],
                "id": int(row["id_desenvolvedor"]),
                "desenvolvedor": row["desenvolvedor"],
                "variabilidade": row["variabilidade"],

                "fa_variabilidade": fa_variabilidade,
                "qtd_commits_arquivo_variabilidade": qtd_commits_arquivo_variabilidade,
                "dl_variabilidade": dl_variabilidade,
                "ac_variabilidade": ac_variabilidade,
                "qtd_arquivos_variabilidade": qtd_arquivos_variabilidade,
                "doav": round(res, 3),
                "doav_n": round(res, 3),
            })


    df = pd.DataFrame(data).sort_values(by=['projeto', 'variabilidade'])
    df['doav_n'] = df.groupby(['projeto', 'variabilidade'])['doav'].transform(lambda x: ((x - x.min())/(x.max() - x.min())))

    df_corte_01 = df[df['doav_n'] > 0.1]
    df_corte_02 = df[df['doav_n'] > 0.15]
    df_corte_03 = df[df['doav_n'] > 0.2]


    out_file = os.path.join(data_dir, "df_corte_01.csv")
    print(out_file)
    df_corte_01.to_csv(out_file, index=False)
    print("[DONE]")

    out_file = os.path.join(data_dir, "df_corte_02.csv")
    print(out_file)
    df_corte_02.to_csv(out_file, index=False)
    print("[DONE]")

    out_file = os.path.join(data_dir, "df_corte_03.csv")
    print(out_file)
    df_corte_03.to_csv(out_file, index=False)
    print("[DONE]")

    out_file = os.path.join(data_dir, "doav.csv")
    with open(out_file, "w", encoding="utf-8") as write_file:
        writer = csv.DictWriter(write_file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    calculate_doav()