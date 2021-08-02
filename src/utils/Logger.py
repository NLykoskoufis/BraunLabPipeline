#!/usr/bin/env python3 
 
import markdown 
from mdtable import MDTable

# ===========================================================================================================
DESC_COMMENT = "Logging function that creates report with various statistics from Pipeline run"
SCRIPT_NAME = "Logger.py"
# ===========================================================================================================

"""
#===============================================================================
@author: Nikolaos Lykoskoufis
@date: 12th of July
@copyright: Copyright 2021, University of Geneva
Logging function that creates report with various statistics from Pipeline run
#===============================================================================
"""

class Log:
    
    def __init__(self, fileName):
        self.fileName = fileName 
        self.log = open(self.fileName, "w")

    def md2html(self,html_output):
        self.log.close()
        f = open(self.fileName,'rt')
        text = f.read()
        html = markdown.markdown(text)
        print(html)
        g = open(html_output, "w")
        g.write(html)
        g.close()
   
    def md2pdf(self):
        return None 
    
    
    def ctitle(self,title, author, date):
        std = f"---\ntitle: {title}\nauthor: {author}\ndate: {date}\ngeometry: margin=2cm\n---\n\n"
        self.log.write(std)
        return None 
    
    def title(self, string):
        std = f"## {string}"
        self.log.write(std)
        self.log.write("\n")
        return None 
    
    def heading1(self,string):
        std = f"### {string}"
        self.log.write(std)
        self.log.write("\n")
        return None 

    def heading2(self,string):
        std = f"#### {string}"
        self.log.write(std)
        self.log.write("\n")
        return None 

    def image(self,title, path):
        std = f"![{title}]({path})"
        self.log.write(std)
        self.log.write("\n")
        
    
    def csv2MDTable(self, fcsv):
        markdown = MDTable(fcsv)
        markdown_string_table = markdown.get_table()
        self.log.write(markdown_string_table)
        self.log.write("\n")
    
    def bold(self,string):
        std = f"**{string}**"
        self.log.write(std)
        self.log.write("\n")
        
    
    def italic(self,string):
        std = f"*{string}*"
        self.log.write(std)
        
    
    def bold_italic(self,string):
        std = f"***{string}***"
        self.log.write(std)
        
    def text(self, string):
        self.log.write(std)
        
    def endl(self):
        self.log.write("\n")
    
    def bullet(self,string):
        std = f"* {string}\n"
        self.log.write(std)
    
    def text(self, string):
        self.log.write(string)
        self.endl()
        
#log = Log("test.md")
#log.ctitle("This is a test","Nikolaos Lykoskoufis","12/07/2021")
#log.title("Title test")        
        
   
    
