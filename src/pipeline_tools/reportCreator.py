#!/usr/bin/env python3 

from os import stat
import pandas as pd 


class HtmlReport(object):
    
    def __init__(self, fout):
        self.fout = fout 
        
    @staticmethod
    def initiate():
        return "<html>\n\n<head>\n  <title>My report!</title>\n  <style>\n    body {\n      background: rgb(58, 58, 58);\n      color: black;\n      font-family: Helvetica Neue, Helvetica, Arial, sans-serif;\n      margin: 0;\n      padding: 0;\n    }\n\n    header {\n      background: #333333;\n      color: white;\n      padding: 50px;\n      text-align: center;\n      height: 100px;\n\n    }\n\n    section {\n      background: white;\n      color: black;\n      padding: 20px;\n\n    }\n\n    footer {\n      font-size: 12px;\n      font-weight: 00px;\n      background: #333333;\n      padding: 10px 20px;\n      color: white;\n    }\n\n    .dataPath {\n      background: #F3F3F3;\n      color: #333333;\n      padding: 5px;\n      border-radius: 5px;\n      display: inline;\n      flex-direction: row;\n      margin: auto;\n    }\n\n    .logList {\n      overflow: auto;\n      line-height: 2;\n      background-color: #F3F3F3;\n      padding-top: 1px;\n      padding-bottom: 25px;\n      width: 100%;\n      height: 100px;\n      position: relative;\n      border-radius: 10px;\n    }\n\n    ul {\n      white-space: nowrap;\n      list-style-type: none;\n      margin: 0;\n      padding: 0;\n    }\n\n    #bamQC {\n      font-size: 13;\n      border-collapse: collapse;\n      margin-left: auto;\n      margin-right: auto;\n    }\n\n    #bamQC td,\n    #bamQC th {\n      border: 1px solid #ddd;\n      padding: 8px 16px;\n      text-align: center;\n      color: black;\n    }\n\n    #bamQC tr:nth-child(even) {\n      background-color: #f2f2f2;\n    }\n\n    #bamQC tr:hover {\n      background-color: #ddd;\n    }\n\n    #bamQC th {\n      padding-top: 12px;\n      padding-bottom: 12px;\n      text-align: center;\n      background-color: #C7DFED;\n      color: black;\n    }\n\n    .myDF {\n      overflow: auto;\n      height: 500px;\n      display: inline-block;\n    }\n\n    .dataframe {\n      overflow: auto;\n      display: inline-block;\n      width: 100%;\n    }\n\n    .myDF thead th {\n      position: sticky;\n      top: 0;\n      z-index: 1;\n    }\n\n    .dataframe thead th {\n      position: sticky;\n      top: 0;\n      z-index: 1;\n    }\n\n    .dfStandards {\n      overflow: auto;\n      display: table-row;\n      width: auto;\n      bottom: 20px;\n    }\n\n    #dfS {\n      font-size: 13;\n      border-collapse: collapse;\n      margin-left: auto;\n      margin-right: auto;\n      text-align: center;\n    }\n\n    #dfS thead {\n      padding-top: 12px;\n      padding-bottom: 12px;\n      text-align: center;\n      background-color: #6699CC;\n      color: black;\n    }\n\n    #dfS td,\n    #dfS th {\n      border: 1px solid black;\n      padding: 8px 16px;\n      text-align: center;\n      color: black;\n    }\n\n\n\n\n\n    .button {\n      display: inline-block;\n      padding: 0.46em 1.6em;\n      border: 0.1em solid #000000;\n      margin: 0 0.2em 0.2em 0;\n      border-radius: 0.12em;\n      box-sizing: border-box;\n      text-decoration: none;\n      font-weight: 500;\n      text-shadow: 0 0.04em 0.04em rgba(0, 0, 0, 0.35);\n      text-align: center;\n      background-color: #337AB8;\n      color: white;\n      text-decoration: none;\n      font-size: 16px;\n      cursor: pointer;\n      transition: all 0.15s;\n      float: right;\n    }\n\n    .button:hover {\n      text-shadow: 0 0 2em rgba(255, 255, 255, 1);\n      color: #FFFFFF;\n      border-color: #FFFFFF;\n    }\n\n    .button2 {\n      display: inline-block;\n      padding: 0.46em 1.6em;\n      border: 0.1em solid #000000;\n      margin: 0 0.2em 0.2em 0;\n      border-radius: 10px;\n      box-sizing: border-box;\n      text-decoration: none;\n      font-weight: 500;\n      text-shadow: 0 0.04em 0.04em rgba(0, 0, 0, 0.35);\n      text-align: center;\n      background-color: #337AB8;\n      color: white;\n      text-decoration: none;\n      font-size: 16px;\n      cursor: pointer;\n      transition: all 0.15s;\n\n    }\n\n    .button2:hover {\n      text-shadow: 0 0 2em rgba(255, 255, 255, 1);\n      color: #FFFFFF;\n      border-color: #FFFFFF;\n    }\n\n    @media all and (max-width:30em) {\n      .button {\n        display: block;\n        margin: 0.4em auto;\n      }\n\n      .button2 {\n        display: block;\n        margin: 0.4em auto;\n      }\n    }\n\n    .mainHeader {\n      font-size: 40px;\n    }\n  </style>\n</head>\n\n"
    
    @staticmethod
    def text(txt, color=None):
        if color == None: 
            return f"<p>{txt}</p>\n"
        else:
            return f"<p style=\"color:{color}\">{txt}</p>\n"
    
    @staticmethod
    def h1(txt):
        return f"<h1>{txt}</h1>\n"
    
    @staticmethod
    def h2(txt):
        return f"<h2>{txt}</h2>\n"
    
    @staticmethod
    def h3(txt):
        return f"<h3>{txt}</h3>\n"
    
    @staticmethod
    def link(text, path):
        return f"<a class=\"button2\" href=\"{path}\">{text}</a>"
    
    
    @staticmethod
    def csv2html(fcsv, classes=None, table_id=None, text_align=None):
        df = pd.read_csv(fcsv)
        return df.to_html(classes=classes, table_id=table_id, justify=text_align)
    
    @staticmethod
    def startBody():
        return "<body>"
    
    @staticmethod
    def endReport():
        return "</body>\n</html>\n"
    
    @staticmethod
    def header(date, path):
        return f"<header>\n\n<a href=\"https://github.com/NLykoskoufis/BraunLabPipeline\" class=\"button\" target=\"_blank\">Github</a>\n<a href=\"https://github.com/NLykoskoufis/BraunLabPipeline/blob/main/README.md\" class=\"button\" target=\"_blank\">Documentation</a>\n<img src=\"reportCreator.png\" style=\"float:left\" height=\"130%\">\n</header>\n\n<section>\n  \n<h1>General information</h1>\n<p>Report generated on 2021-11-17, 10:30 based on data in:</p>\n<div class=\"dataPath\">/srv/beegfs/scratch/shares/brauns_lab/data/nikos/mouseBrainMetabolism/data_raw/ATACseq2</div></section>"
    
    @staticmethod
    def addPathWithBackground(path):
        return f"<div class=\"dataPath\">{path}</div>\n"
    
    @staticmethod
    def addImage(path, title):
        return f"<embed src=\"{path}\" alt=\"{title}\" width=\"800px\" height=\"800px\">\n"
        
        
    @staticmethod
    def footer():
        return "<footer>\n <p>Created by Nikolaos Lykoskoufis and Simon Braun <span>&copy</span> 2021</p> \n <p>Contact: <a style=\"color:inherit\" href=\"mailto:nikolaos.lykoskoufis@unige.ch\">nikolaos.lykoskoufis@unige.ch</a>, <a style=\"color:inherit\" href=\"mailto:simon.braun@unige.ch\">Simon.Braun@unige.ch</a></p>\n</footer>\n"
    

    def writeToFile(self,htmlCode):
        with open(self.fout, "w") as g: 
            g.write(htmlCode)
    
    class SectionCreator():
        @staticmethod
        def initiateSection():
            return "<section>\n"
        
        @staticmethod
        def terminateSection():
            return "</section>\n"  
    
    class listCreator():
        
        @staticmethod
        def initiateList(classes):
            return f"<div class=\"{classes}\">\n<nav>\n<ul>\n"
        
        @staticmethod
        def terminate():
            return "</ul>\n</nav>\n</div>"
            
        @staticmethod
        def addElement(txt, color=None):
            if color == None: 
                return f"<li>{txt}</li>"
            else:
                return f"<li style=\"color:{color}\">{txt}</li>"
        
    
