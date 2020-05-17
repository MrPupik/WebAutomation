from pymongo import MongoClient
from selenium.common.exceptions import WebDriverException
from time import sleep
from pathlib import Path
from os.path import dirname
from json import dumps, loads
from izSelenium.Core.Logger import log

session_file = Path(f"{dirname(__file__)}/../data/sessions.json")

def read_all_sessions():
    try:
        return list(loads(session_file.read_text()))
    except Exception as err:
        log.error(f"sessions file corrupted at {session_file.absolute()}")
        raise err

def get_open_sessions(driver_url, webdriver_class, desired_capabilities):
    saved_sessions = read_all_sessions()
    deactive_sessions_ids = []
    active_sessions = {}
    active_sessions_ids = []
    
    for session in saved_sessions:
        try:
            driver = webdriver_class(driver_url, desired_capabilities)
            driver.close()
            driver.quit()
            sleep(0.12)
            driver.session_id = session['id']
            driver.current_url
            active_sessions[session['alias']] = driver
            active_sessions_ids.append(driver.session_id)
        except WebDriverException:
            deactive_sessions_ids.append(session['id'])
            _delete_sessions(deactive_sessions_ids)   
    return active_sessions, active_sessions_ids, deactive_sessions_ids

def close_open_sessions(driver_url,webdriver_class, desired_capabilities):
    try:
        active_sessions, active_sessions_ids, deactive = get_open_sessions(driver_url, webdriver_class, desired_capabilities)
        for session in active_sessions.values():
            session.close()
            session.quit()      
    except Exception as err:
        log.warning("couldnt close open sessions.")
        log.debug(err)
    with open(session_file.absolute(), 'w') as f:        
        f.write('[]')
    

def _delete_sessions(sessions_ids: list):
    try:
     
        with open(session_file.absolute(), 'r+') as f:
            session_list = list(loads(f.read()))          
            f.seek(0)        
            f.write('[]')
            f.truncate()
    except Exception as err:
        log.warning("couldnt save drvier session.")
        log.debug(err)


def save_session(alias, session_id):
    try:
        with open(session_file.absolute(), 'r+') as f:
            session_list = list(loads(f.read()))
            session_list.append({
                "id": session_id,
                "alias": alias
            })    
            f.seek(0)        
            f.write(dumps(session_list))
            f.truncate()
    except Exception as err:
        log.warning("couldnt save drvier session.")
        log.debug(err)