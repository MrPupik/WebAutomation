from pymongo import MongoClient
from selenium.common.exceptions import WebDriverException
from time import sleep
mongo = None
client = None
webdriver_collection_name = 'webdriver'


def connect():
    global mongo
    global client
    if not mongo:
        MONGODB_URL = 'dbetaruns0002'
        DB = "TestData"
        client = MongoClient(MONGODB_URL, port=27017)
        mongo = client[DB]
    return mongo


def get_open_sessions(driver_url, webdriver_class, desired_capabilities):    
    mongo = connect()
    sessions = list(mongo[webdriver_collection_name].find({}))
    deactive_sessions_ids = []
    active_sessions = {}
    active_sessions_ids = []
    for session in sessions:        
        try:
            driver = webdriver_class(driver_url, desired_capabilities)
            driver.close()
            driver.quit()
            sleep(0.1)
            driver.session_id = session['_id']
            driver.current_url
            active_sessions[session['alias']] = driver
            active_sessions_ids.append(driver.session_id)
        except WebDriverException:
            deactive_sessions_ids.append(session['_id'])    
    return active_sessions, active_sessions_ids, deactive_sessions_ids

def close_open_sessions(driver_url,webdriver_class, desired_capabilities):
    active_sessions, active_sessions_ids, deactive = get_open_sessions(driver_url, webdriver_class, desired_capabilities)
    for session in active_sessions.values():
        session.close()
        session.quit()
    _delete_sessions(active_sessions_ids + deactive)


def _delete_sessions(sessions_ids: list):
    mongo = connect()
    mongo[webdriver_collection_name].delete_many({"_id": {"$in": sessions_ids}})


def save_session(alias, session_id):
    connect()[webdriver_collection_name].insert({'alias':alias,'_id':session_id})
    global client
    client.close()