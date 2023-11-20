import os
import csv
import json

import pandas as pd

from tqdm import tqdm


working_directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
repositories = os.path.join(working_directory, "data", "repositories")


def parse_files():

    with os.scandir(repositories) as it:
        first = True

        for entry in it:
            name, ext = os.path.splitext(entry.name)
            repo = name.split("/")[-1]

            if ext == ".csv":
        
                commit = ""
                type = ""
                date = ""

                data = []
                counters = {
                    "repo": repo,
                    "Especialista": 0,
                    "Generalista": 0,
                    "Misto": 0,
                }

                print(f"Opening file: {entry.name}... ")
                with open(entry) as csv_file:
                    reader = csv.DictReader(csv_file)

                    #print(f"Sorting file: {entry.name}... ", end="")
                    #reader = sorted(csv_reader, key=lambda row: row["Commit"])
                    #print("[DONE]")
                    for row in tqdm(reader, "Traversing repository [%s]" % repo):

                        if commit != row["Commit"]:

                            if commit != "":
                                data.append({
                                    "repo": repo,
                                    "commit": commit,
                                    "date": date[:7],
                                    "type": type
                                })

                                counters[type] += 1

                            type = ""
                            commit = row["Commit"]
                            date = row["Data"].split(" ")[0]


                        if row["Variabilidade"] == "TRUE":
                            if type == "Especialista":
                                type = "Misto"
                            else:    
                                type = "Generalista"
                        elif type == "Generalista":
                            type = "Misto"
                        else:
                            type = "Especialista"

                print("Saving file: commits_type.csv... ", end="")
                with open("commits_type.csv", "a") as output_csv:
                    dict_writer = csv.DictWriter(output_csv, data[0].keys())
                    if first:
                        first = False
                        dict_writer.writeheader()

                    dict_writer.writerows(data)
                print("[DONE]")

                df = pd.DataFrame(data)
                print("Counting... ")
                result = df.groupby(["repo", "date", "type"]).count()
                result.to_csv("teste.csv", mode='a', header=not os.path.exists("teste.csv"))

                with open("commits_type.txt", "a") as output_txt:
                    output_txt.write(json.dumps(counters))
                    output_txt.write("\n")


if __name__ == "__main__":
    parse_files()
