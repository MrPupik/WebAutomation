import sys
this =sys.modules[__name__]
import io
import csv
from enum import Enum
import allure
from allure_commons.types import AttachmentType
from sys import stdout as st

this.writer = print

def _silent(msg:str):
    pass

def Quiet():
    """
    disable logs
    """
    this.writer = _silent
def Noise():
    """
    enable logs
    """
    this.writer = print


class Bug():
    def __init__(self,category, description, expected, actual):
        self._cat = category
        self._desc = description
        self._exp = expected
        self._act = actual

    def toList(self):
        return [self._cat, self._desc, self._exp,self._act]


this.bugs = []


#region test manager

def attach_screenshot(picname="Screenshot", driver=None):
    """
    add screenshot to current step at allure-report
    """
    allure.attach(driver.get_screenshot_as_png(), name=picname,attachment_type=AttachmentType.PNG)


def attach_bugs():
    """
    attach all bugs from logger to current step at allure-report
    """
    allure.attach(bugs_to_csv(), name="step bugs", attachment_type=AttachmentType.CSV)



def add_bug(category, expected, actual, description=""):
    """
    logs a fail and saves what happend in bug list
    *** bugs are not saved at the moment *** 
    """
    fail(category+":\n"+" expected: "+expected+"\nactual:"+actual)
    fail(description)
    this.bugs.append(Bug(category, description, expected, actual)) # TODO bugs are not saved at the moment    

def bugs_to_csv():
    stream = io.StringIO()
    wr = csv.writer(stream)
    for bug in bugs:
        wr.writerow(bug.toList())
    return stream.getvalue()


#endregion



def _cust(msg:str, mark:str):
    """
    costumise print - format: {mark} {msg} {mark}
    """       
    try:
        this.writer(mark+" "+str(msg)+" "+mark)
    except UnicodeEncodeError:
        this.writer(mark+" "+str(msg).encode('ascii','backslashreplace').decode('ascii')+" "+mark)
    except Exception as e:
        Error('LOGGER EXCEPTION')
        Error(e)


def error(msg:str):
    """
    something went wrong, but it's not a bug in the tested system
    """    
    _cust(msg, "-err-")

def fail(msg:str):
    _cust(msg, "-xx-")
def success(msg:str):
    _cust(msg, "-vv-")    
def info(msg:str):
    this.writer("    ")
    _cust(msg, "-i-")  
def warn(msg:str):
    _cust(msg, "-!-")  

def title(msg:str):
    this.writer('\n')
    _cust(msg, " -- ")
    this.writer('\n')

def std(msg:str):
    if this.writer is _silent:
        return None
    st.write(msg)
    st.flush()