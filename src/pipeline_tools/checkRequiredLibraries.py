#!/usr/bin/env python3 

# ===========================================================================================================
DESC_COMMENT = "ATACseq pipeline"
SCRIPT_NAME = "checkRequiredLibraries.py"
# ===========================================================================================================

"""
#===============================================================================
@author: Nikolaos Lykoskoufis
@date: 7th of July
@copyright: Copyright 2021, University of Geneva
Scripts that checks whether all necessary libraries are installed for pipeline to work. 
#===============================================================================
"""

import sys
import subprocess
import pkg_resources
import os 

pipeline_path = sys.path[0].replace("pipeline_tools", "")
print(pipeline_path)
utils_tools_path = os.path.abspath(pipeline_path+"/utils")
sys.path.append(utils_tools_path)
from verbose import verbose as vrb

vrb.bullet("Checking libraries")



required = {'json', 'glob','argparse','smtplib','email.mime.text','markdown','mdtable'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed
print(missing)
if missing:
    python = sys.executable
    subprocess.check_call(['pip3', 'install','--user', *missing], stdout=subprocess.DEVNULL)# the install function from the question
else:
    vrb.bullet("All necessary libraries are installed.")