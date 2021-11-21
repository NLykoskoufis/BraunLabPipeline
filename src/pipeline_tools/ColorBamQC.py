#!/usr/bin/env python3 
from collections import defaultdict


def PBC1(technology,value):
    if technology == "ATACseq":
        if float(value) < 0.7: 
            return "orange"
        elif float(value) <= 0.9 and float(value) >= 0.7:
            return "yellow"
        else: 
            return "#4dbd4d"
    elif technology == "ChIPseq":
        if float(value) < 0.5:
            return "orange"
        elif float(value) < 0.8 and float(value) >= 0.5:
            return "yellow" 
        elif float(value) < 0.9 and float(value) >= 0.8:
            return "#4dbd4d"
        else: 
            return "#4dbd4d"
    else: 
        print("These metrics only work with ATACseq or ChIPseq.")

def PBC2(technology,value):
    if technology == "ATACseq":
        if float(value) < 0.1: 
            return "orange"
        elif float(value) <= 3 and float(value) >= 1:
            return "yellow"
        else: 
            return "#4dbd4d"
    elif technology == "ChIPseq":
        if float(value) < 1:
            return "orange"
        elif float(value) < 3 and float(value) >= 1:
            return "yellow"
        elif float(value) < 10 and float(value) >= 3:
            return "#4dbd4d"
        else: 
            return "#4dbd4d"
    else: 
        print("These metrics only work with ATACseq or ChIPseq.")
        
def NRF(technology,value):
    if technology == "ATACseq":
        if float(value) < 0.7: 
            return "orange"
        elif float(value) <= 0.9 and float(value) >= 0.7:
            return "yellow"
        else: 
            return "#4dbd4d"
    elif technology == "ChIPseq":
        if float(value) < 0.5:
            return "orange"
        elif float(value) < 0.8 and float(value) >= 0.5:
            return "yellow"
        elif float(value) < 0.9 and float(value) >= 0.8:
            return "#4dbd4d"
        else: 
            return "#4dbd4d"
    else: 
        print("These metrics only work with ATACseq or ChIPseq.")
        
def readCSV(fcsv):
    lst = []
    with open(fcsv, "rt") as f: 
        for line in (line.rstrip().split(",") for line in f):
            lst.append(line)
    return lst


def csvtoHTML(file):
    lst = readCSV(file)
    html = ""
    html += "<table border=\"1\" class=\"myDF\" id=\"bamQC\">\n"
    html += "<thead>\n"
    html += "<tr style=\"text-align: center;\">\n<th></th>\n"
    for i in lst[0]:
        html += f"<th>{i}</th>\n"

    html += "</tr>\n</thead>\n<tbody>\n"
    for i in range(1,len(lst)):
        html += "<tr>\n"
        for j in range(len(lst[i])):
            if j == 0: 
                html += f"<td>{lst[i][j]}</td>\n"
            if j == 4: 
                color = NRF("ATACseq",lst[i][j])
                html += f"<td style=\"background-color:{color}; font-weight:bold\">{lst[i][j]}</td>\n"
            elif j == 5: 
                color = PBC1("ATACseq",lst[i][j])
                html += f"<td style=\"background-color:{color}; font-weight:bold\">{lst[i][j]}</td>\n"
            elif j == 6: 
                color = PBC2("ATACseq",lst[i][j])
                html += f"<td style=\"background-color:{color}; font-weight:bold\">{lst[i][j]}</td>\n"
            else: 
                html += f"<td>{lst[i][j]}</td>\n"

        html += "</tr>\n"
    html += "</tbody>\n</table>"

    return html

