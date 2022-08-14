#!/usr/bin/env python
# -*- coding: utf-8 -*-

def create_arquivo(id_commit, author_name, author_email, file_name, date, variabilities):
    file_data = {}
    file_data["Autores"] = {}
    file_data["Commits"] = {}
    file_data["Variabilidades"] = {}

    commit = id_commit + "  -  " + date
    aname = author_name + "  -  " + date

    file_data["Autores"][author_name] = {}
    file_data["Autores"][author_name]["Variabilidades"] = variabilities
    file_data["Autores"][author_name]["Commits"] = [ commit ]
    
    file_data["Commits"][id_commit] = {}
    file_data["Commits"][id_commit]["Variabilidades"] = variabilities
    file_data["Commits"][id_commit]["Autores"] = [ aname ]

    for var in variabilities:
        file_data["Variabilidades"][var] = {}
        file_data["Variabilidades"][var]["Autores"] = [ author_name ]
        file_data["Variabilidades"][var]["Commits"] = [ commit ]

    return file_data


def update_arquivo(file_data, id_commit, author_name, author_email, file_name, date, variabilities):
    """
    """

    commit = id_commit + "  -  " + date
    aname = author_name + "  -  " + date

    if author_name in file_data["Autores"]:
        for var in variabilities:
            if var not in file_data["Autores"][author_name]["Variabilidades"]:
                file_data["Autores"][author_name]["Variabilidades"].append(var)

        if commit not in file_data["Autores"][author_name]["Commits"]:
            file_data["Autores"][author_name]["Commits"].append(commit)
    else:
        file_data["Autores"][author_name] = {}
        file_data["Autores"][author_name]["Variabilidades"] = variabilities
        file_data["Autores"][author_name]["Commits"] = [ commit ]

    if id_commit in file_data["Commits"]:
        for var in variabilities:
            if var not in file_data["Commits"][id_commit]["Variabilidades"]:
                file_data["Commits"][id_commit]["Variabilidades"].append(var)
        
        if aname not in file_data["Commits"][id_commit]["Autores"]:
            file_data["Commits"][id_commit]["Autores"].append(aname)
    else:
        file_data["Commits"][id_commit] = {}
        file_data["Commits"][id_commit]["Variabilidades"] = variabilities
        file_data["Commits"][id_commit]["Autores"] = [ aname ]

    for var in variabilities:
        if var in file_data["Variabilidades"]:
            if author_name not in file_data["Variabilidades"][var]["Autores"]:
                file_data["Variabilidades"][var]["Autores"].append(author_name)
            
            if commit not in file_data["Variabilidades"][var]["Commits"]:
                file_data["Variabilidades"][var]["Commits"].append(commit)
        else:
            file_data["Variabilidades"][var] = {}
            file_data["Variabilidades"][var]["Autores"] = [ author_name ]
            file_data["Variabilidades"][var]["Commits"] = [ commit ]

    return file_data