#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import csv
import sys
import imp
import traceback

class Preprocessor:

    def __init__(self):
        """
        """
        # private variables
        self.__linenum = 0


    def lexer(self, line):
        """
        """

        var = ''
        found = 0
        directive = ''

        # handle #ifdef directives
        if line.startswith('#ifdef'): # Pode ter apenas 1 parâmetro
            directive = '#ifdef'
            found = 1
        # handle #ifndef directives (is the same as: #ifdef X #else)
        elif line.startswith('#ifndef'): # Pode ter apenas 1 parâmetro
            directive = '#ifndef'
            found = 1
        # handle #if directives
        elif line.startswith('#if'):
            if "defined" in line:
                directive = '#if'
                found = 3
                aux = line[3:].split("defined")
                var = "".join(aux)
            else:
                found = 0
        # handle #elif directives
        elif line.startswith('#elif'):
            directive = '#elif'
            found = 1
        # handle #else directives
        elif line.startswith('#else'):
            directive = '#else'
            found = 0
        elif line.startswith("#"):
            found = 0
        elif not line:
            found = 0
        else:
            found = 2
            var = "TRUE"

        if found == 1:
            var = " ".join(line.split(directive))

        return found, directive, var.strip()


    def parse_save(self, in_file, out_file, commit, data, autor, email, file_name):
        """

        """
        csv_buffer = []
        output_buffer = []
        variabilities = []

        with open(in_file) as input_file:
            for line in input_file:
                self.__linenum += 1

                if line[0] != '+' and line[0] != '-':
                    continue
                
                found, prep, var = self.lexer(line[1:].strip())
                
                if found != 0:
                    output_buffer.append({
                        "line": self.__linenum,
                        "modification": line[0],
                        "preprocessor": prep,
                        "var": var
                    })

                    csv_buffer.append({
                        "Commit": commit,
                        "Data": data,
                        "Autor": autor,
                        "Email": email,
                        "Arquivo": file_name,
                        "Mudanca por arquivo": line[0],
                        "Variabilidade": var,
                        "Mudanca por variabilidade": line[0]
                    })

                    if var not in variabilities:
                        variabilities.append(var)
        
        
        if len(output_buffer) != 0:
            with open(out_file, 'w+') as output_file:
                dict_writer = csv.DictWriter(output_file, ["line", "modification", "preprocessor", "var"])
                dict_writer.writeheader()
                
                dict_writer.writerows(output_buffer)

        return sorted(variabilities), csv_buffer


    def parse(self, in_file):
        """

        """
        variabilities = []

        with open(in_file) as input_file:
            for line in input_file:
                self.__linenum += 1

                if line[0] != '+' and line[0] != '-':
                    continue
                
                found, prep, var = self.lexer(line[1:].strip())
                
                if found != 0 and var not in variabilities:
                    variabilities.append(var)

        return sorted(variabilities)