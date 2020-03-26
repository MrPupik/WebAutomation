import Autotest.Core.Logger as log
import Autotest.Core.TimeoutManager as tm
#region open/close app
# from selenium.webdriver import Chrome
from time import sleep
import Autotest.WebDriver.Selectors.chrome as chrome

POPUPS_ALLOWED = False

def AllowPopups(webdriver,SERVER):
    """
    this function will be removed some day, please use allowPopus
    """
    return allowPopups(webdriver,[SERVER])

def allowPopups(webdriver, SERVERS:list):
    """
    recives a list of domain urls, and modify chrome settings to use popups
    """
    log.title("allow system to use pop up ")
    log.info("-- add pop-ups domains to chrome settings --")
    driver = webdriver
    # share webdriver with chrome-slelectors
    chrome.driver = webdriver
    driver.get(chrome.URL_SETTINGS)
    driver.maximize_window()
    driver.switch_to_frame("settings")
    chrome.lblAdvanced().click()
    sleep(0.05)
    chrome.btnPrivacy().click()
    sleep(0.2)
    chrome.btnPopupException().scroll_into_view()
    sleep(0.05)
    chrome.btnPopupException().click()
    sleep(0.1)
    inpt = chrome.inptHostname()
    for i in range(0, 2):
        all_in = True
        for url in SERVERS:
            inpt.click()
            sleep(0.05)
            inpt.send_keys(url)
            sleep(0.1)
            chrome.frmAdd_exc().click()
            sleep(0.1)
            if not chrome.txtAdded(url):
                all_in = False
        tm.Short_timeout()
        if all_in:
            chrome.btnConfirmException().click()
            sleep(0.1)
            chrome.btnConfirmSettings().click()
            log.success("chrome popups allowed")
            log.info("i saw system's url at chrome exception screen !")
            POPUPS_ALLOWED = True
            return True
        else:
            log.warn('i missed something, couldnt find systems url as an exception')
    log.fail('couldnt find systems url as an exception at the 2nd time')
    POPUPS_ALLOWED = False
    return False
    # d.switch_to_frame("settings")
