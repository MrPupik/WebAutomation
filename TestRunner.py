import sys
import Core.izHelpers as stuff
import subprocess
import os 
import shutil
from Core.izHelpers import Command, CommandSequence

Windows_Paths = {
    "tower":"c:\\AutoTest\\Tower",
    "autotest": "C:\\AutoTest\\Autotest",
    "memento": "C:\\AutoTest\\Memento",
    "isight": "C:\\AutoTest\\iSight",
    "loki": "C:\\AutoTest\\Loki",
    }

Linux_Paths = {
    "tower":"/home/administrator/AutoTest/Tower",
    "autotest": "/home/administrator/AutoTest/Autotest",
    "memento": "/home/administrator/AutoTest/Memento",
    "isight": "/home/administrator/AutoTest/iSight",
    "loki": "/home/administrator/AutoTest/Loki",
    }

from platform import platform

if 'Windows' in platform():
    Paths = Windows_Paths
else:
    Paths = Linux_Paths

params, flags = stuff.processArgs(sys.argv)

if ('-a' not in params.keys()) or ('-h' in flags):
    print("""
    Test Runner: runs pytest and serve allure report
    -a      tested application name
    -t      [OPTIONAL] *relative* path to tests. default: /tests
    -d      [OPTIONAL] path allure-results data folder, defualt: /Allure/Results
    -r      [OPTIONAL] path for reports (for history trends), default: /Allure/Rreport
    -h      show this help
    """)
    sys.exit(1)

app_path = Paths[str(params['-a']).lower()]

def vals(defaults:dict,parms:dict, base:str):
    # handle args vs default values
    results = ()
    for k,v in defaults.items():
        if k in params.keys():
            results+=(base+"\\"+params[k])
        else:
            results = results + (str(base+"\\"+v),)
    return results

stuff = {'-t':'tests', '-d':'Allure\\Results', '-r':'Allure\\Reports'}
dir_test, dir_results, dir_reports = vals(stuff,params,app_path)
# dir_test = app_path+""
# dir_results = app_path+"/allure-results"
# dir_reports = app_path+"/allure-reports"

# if '-t' in params.keys():
#     dir_test=params['-t']
# else:
#     dir_test=app_path+"/tests
# if '-o' in params.keys():
#     dir_reports+=params['-o']
# if '-r' in params.keys():
#     dir_results+=params['-r']



cmd_pytest = Command("pytest --alluredir="+dir_results+" "+ dir_test)
history = dir_reports+"\history"
dest = dir_results+"\history"

if os.path.exists(dir_results):
    shutil.rmtree(dir_results)
os.mkdir(dir_results)
if os.path.exists(history):
    shutil.move(src=history,dst=dir_results)
    # cmd_History = Command(str("xcopy "+history +" "+dir_results+)
# cmd_clearOld = ""

with open('tmp.bat', 'w+') as file:
    file.writelines(["allure generate -c -o "+dir_reports+" "+dir_results])
# cmd_allureGen = Command("C:\\Users\\itayz\\scoop\\shims\\allure.bat generate -c -o "+dir_reports+" "+dir_results)
# cmd_allureServe = Command("C:\\Users\\itayz\\scoop\\shims\\allure open "+dir_reports)
cmd_bat = Command("tmp.bat")
seq = CommandSequence(cmd_pytest,cmd_bat)
seq.execute()
with open('tmp.bat', 'w') as file:
    file.writelines(["allure open "+dir_reports])
try:
    cmd_bat.execute()
except:
    pass
finally:
    os.remove('tmp.bat')
