#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re  # biblioteca expressão regular
import math

from dateutil.parser import *

from utils import str_split

	
def ownership_rlm (qtd_commits_ac, ownership_n, qtd_commits_dl):
	"""
	Calcula e retorna o ownership utilizando os parâmetros da regressão linear múltipla
	:param qtd_commits_ac: quantidade de commits aceitos que outros desenvolvedores realizaram
	:param ownership_n: quantidade de alterações normalizadas no arquivo
	:param qtd_commits_dl: quantidade de commits aceitos
	"""
	total = 0.33632 - 0.10765 * math.log(1 + qtd_commits_ac) + 0.59917 * ownership_n + 0.06737 * math.log(1 + qtd_commits_dl)
	return total


def ownership_arquivo_perc (rows):
	"""
	Calcula e retorna a porcentagem de ownership do arquivo 
	:param rows: linhas do csv
	"""
	dict_arquivo = dict()

	for r in rows:
		if r['arquivo'] not in dict_arquivo:
			dict_arquivo[r['arquivo']] = r['ownership_arquivo']
		else:
			dict_arquivo[r['arquivo']] += r['ownership_arquivo']


	for r in rows:
		r['ownership_arquivo_perc'] = 100 * r['ownership_arquivo'] / dict_arquivo[r['arquivo']]

	return rows


def parse_variability(json_data):
	rows = []
	
	dict_ownership_r = dict()
	dict_ownership_arquivo = dict()
	for varname, vardata in json_data['Variabilidades'].items():

		end = 0
		begin = 0
		vrows = []
		variadic = dict()
		filedict = dict()
		ownerdict = dict()
		totaldict = dict()
		qtd_commits_geral = 0

		if varname == "TRUE":
			continue;

		for id_commit, commitdata in vardata['Commits'].items():
			for filename in commitdata['Arquivos']:
				fname = str_split(filename)

				if id_commit in json_data['Commits']:
					files = json_data['Commits'][id_commit]['Arquivos']
					if fname in files:
					
						varcount = 0
						for var in files[fname]['Variabilidades']:
							vname = str_split(var)

							if varname == vname:
								varcount += 1

								if fname in filedict:
									aux = filedict[fname]
									aux += varcount
									filedict[fname] = aux
								else:
									filedict[fname] = varcount

								if vname in totaldict:
									totaldict[vname] += 1
								else:
									totaldict[vname] = 1

		nfiles = len(filedict)
		for fname in filedict:
			qtd_commits_geral += filedict[fname]

		for authorname, authordata in vardata['Autores'].items():

			begin = end
			qtd_commits_dl = 0
			ownership_geral = 0

			for filename in authordata['Arquivos']:
				fname = str_split(filename)

				valid_file = False
				ownership = 0
				qtd_commits_arquivo = 0

				for commit in authordata['Commits']:
					id_commit = str_split(commit)

					if id_commit in json_data['Commits']:

						files = json_data['Commits'][id_commit]['Arquivos']
						if fname in files:

							valid_commit = False
							for var in files[fname]['Variabilidades']:
								if varname == str_split(var):
									valid_commit = True
									ownership += 1
									ownership_geral += 1

							if not valid_commit:
								continue

							valid_file = True
							qtd_commits_arquivo += 1
							qtd_commits_dl += 1

							#data_commit = re.search('\(([^)]+)', commit).group(1)
							data_commit = commit.split("  -  ")[1]
							data_commit = parse(data_commit.strip(), ignoretz=True)

							if fname in dict_ownership_arquivo:
								fcount = dict_ownership_arquivo.get(fname)

								fcount += 1
								# Calcula o ownership do arquivo 
								dict_ownership_arquivo[fname] = fcount
							else:
								dict_ownership_arquivo[fname] = 1

							if fname in ownerdict:
								author, criacao, own = ownerdict.get(fname)

								if data_commit < criacao:
									author = authorname
									criacao = data_commit

								if ownership > own:
									own = ownership

								ownerdict[fname] = (author, criacao, own)
							else:
								ownerdict[fname] = (authorname, data_commit, ownership)


							if varname in variadic:
								author, criacao, own = variadic.get(varname)

								if data_commit < criacao:
									author = authorname
									criacao = data_commit

								if ownership_geral > own:
									own = ownership_geral

								variadic[varname] = (author, criacao, own)
							else:
								variadic[varname] = (authorname, data_commit, ownership_geral)

				if valid_file:
					try:
						ownership_perc = (ownership / filedict[fname]) * 100

						vrows.append({
							"desenvolvedor": authorname,
							"variabilidade": varname,
							"fa_geral": 0,
							"qtd_commits_geral": qtd_commits_geral,
							"qtd_commits_dl": qtd_commits_dl,
							"qtd_commits_ac": qtd_commits_geral,
							"qtd_arquivos": nfiles,
							"arquivo": fname,
							"qtd_commits_arquivo": qtd_commits_arquivo,
							"fa_arquivo": 0,
							"ownership_perc": round(ownership_perc, 3),
							"ownership_n": ownership,
							"ownership_geral": 0,
							"ownership_geral_n": 0,
							"ownership_arquivo": dict_ownership_arquivo[fname],
							"ownership_arquivo_n": 0,
							"ownership_arquivo_perc": 0,
							"ownership_rlm": 0,
							"ownership_rlm_n": 0,
						})

						end += 1

					except Exception as err:
						print(varname, filedict)
						print(authorname, fname)
						print("Exception: ", err)

			for i in range(begin, end):
				if vrows[i]['qtd_commits_ac'] - qtd_commits_dl < 0:
					vrows[i]['qtd_commits_ac'] = 0
				else:
					vrows[i]['qtd_commits_ac'] -= qtd_commits_dl
                    
				vrows[i]['qtd_commits_dl'] = qtd_commits_dl
				vrows[i]['ownership_geral'] = ownership_geral
				vrows[i]['ownership_geral_n'] = ownership_geral

		for r in vrows:
			author, criacao, ownership = ownerdict.get(r['arquivo'])
			if r['desenvolvedor'] == author:
				r['fa_arquivo'] = 1

			r['ownership_n'] /= ownership
			r['ownership_n'] = round(r['ownership_n'], 3)

			author, criacao, ownership = variadic.get(r['variabilidade'])
			if r['desenvolvedor'] == author:
				r['fa_geral'] = 1

			r['ownership_geral'] = (r['ownership_geral'] / totaldict[r['variabilidade']]) * 100
			r['ownership_geral_n'] /= ownership

			r['ownership_geral'] = round(r['ownership_geral'], 3)
			r['ownership_geral_n'] = round(r['ownership_geral_n'], 3)

			try:
				r['ownership_rlm'] = ownership_rlm(r['qtd_commits_ac'], r['ownership_n'], r['qtd_commits_dl'])
			except Exception as err:
				print("Exception: ", err)
				print(r['desenvolvedor'], r['variabilidade'], r['arquivo'])
				print(r["qtd_commits_ac"], r["ownership_n"], r["qtd_commits_dl"])
				continue
			
			if r['arquivo'] in dict_ownership_arquivo:
				ownership_arquivo = dict_ownership_arquivo.get(r['arquivo'])

				if r['ownership_arquivo'] > ownership_arquivo:
					ownership_arquivo = r['ownership_arquivo']

				dict_ownership_arquivo[r['arquivo']] = ownership_arquivo
			else:
				dict_ownership_arquivo[r['arquivo']] = r['ownership_arquivo']


			if r['variabilidade'] in dict_ownership_r:
				ownership_rlm = dict_ownership_r.get(r['variabilidade'])

				if r['ownership_rlm'] > ownership_rlm:
					ownership_rlm = r['ownership_rlm']

				dict_ownership_r[r['variabilidade']] = ownership_rlm
			else:
				dict_ownership_r[r['variabilidade']] = r['ownership_rlm']

			rows.append(r)

		for r in rows:
			ownership_rlm = dict_ownership_r.get(r['variabilidade'])
			r['ownership_rlm_n'] = r['ownership_rlm'] / ownership_rlm

			ownership_arquivo = dict_ownership_arquivo.get(r['arquivo'])
			r['ownership_arquivo_n'] = r['ownership_arquivo'] / ownership_arquivo

	return ownership_arquivo_perc(rows)


def create_variability(id_commit, author_name, author_email, file_name, date, var_name):
    var_data = {}
    var_data["Autores"] = {}
    var_data["Commits"] = {}
    var_data["Arquivos"] = {}

    commit = id_commit + "  -  " + date
    aname = author_name + "  -  " + date

    var_data["Autores"][author_name] = {}
    var_data["Autores"][author_name]["Arquivos"] = [ file_name ]
    var_data["Autores"][author_name]["Commits"] = [ commit ]

    var_data["Commits"][id_commit] = {}
    var_data["Commits"][id_commit]["Arquivos"] = [ file_name ]
    var_data["Commits"][id_commit]["Autores"] = [ aname ]

    var_data["Arquivos"][file_name] = {}
    var_data["Arquivos"][file_name]["Autores"] = [ author_name ]
    var_data["Arquivos"][file_name]["Commits"] = [ commit ]

    return var_data


def update_variability(var_data, id_commit, author_name, author_email, file_name, date, var_name):    
    commit = id_commit + "  -  " + date
    aname = author_name + "  -  " + date

    if author_name in var_data["Autores"]:
        if file_name not in var_data["Autores"][author_name]["Arquivos"]:
            var_data["Autores"][author_name]["Arquivos"].append(file_name)
            
        if commit not in var_data["Autores"][author_name]["Commits"]:
            var_data["Autores"][author_name]["Commits"].append(commit)
    else:
        var_data["Autores"][author_name] = {}
        var_data["Autores"][author_name]["Arquivos"] = [ file_name ]
        var_data["Autores"][author_name]["Commits"] = [ commit ]

    if id_commit in var_data["Commits"]:
        if file_name not in var_data["Commits"][id_commit]["Arquivos"]:
            var_data["Commits"][id_commit]["Arquivos"].append(file_name)

        if aname not in var_data["Commits"][id_commit]["Autores"]:
            var_data["Commits"][id_commit]["Autores"].append(aname)
    else:
        var_data["Commits"][id_commit] = {}
        var_data["Commits"][id_commit]["Arquivos"] = [ file_name ]
        var_data["Commits"][id_commit]["Autores"] = [ aname ]

    if file_name in var_data["Arquivos"]:
        if author_name not in var_data["Arquivos"][file_name]["Autores"]:
            var_data["Arquivos"][file_name]["Autores"].append(author_name)

        if commit not in var_data["Arquivos"][file_name]["Commits"]:
            var_data["Arquivos"][file_name]["Commits"].append(commit)
    else:
        var_data["Arquivos"][file_name] = {}
        var_data["Arquivos"][file_name]["Autores"] = [ author_name ]
        var_data["Arquivos"][file_name]["Commits"] = [ commit ]
    
    return var_data