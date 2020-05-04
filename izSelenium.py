

# region  imports 
import sys
from platform import platform
from os import path
import types
from time import sleep
from collections import namedtuple
from json import loads, dumps, JSONDecodeError

# selenium
import selenium.webdriver as webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import selenium.webdriver.remote.webelement as webelement
from selenium.webdriver.common.by import By
import selenium.webdriver.common.action_chains as actions
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoSuchElementException


# Autotest
from Autotest.Core.izHelpers import actionWrapper
import Autotest.Core.TimeoutManager as TM
import Autotest.Core.Logger as log
from Autotest.WebDriver.session_manager import close_open_sessions, save_session, get_open_sessions

# endregion


# config
this = sys.modules[__name__]
CONFIG_PATH = path.dirname(__file__)+"/iz.conf"

def _read_config():
    global CONFIG_PATH
    try:
        with open(CONFIG_PATH, 'r') as conf_file:
            this.conf = loads(conf_file.read())
            this._webdriver_url = conf['webdriver-url'].replace('\n','')
            this.debug_mode = conf['debug-mode'] if 'debug-mode' in conf.keys() else True
    except Exception as Error:
        log.error(f'error reading config file at {CONFIG_PATH}')
        raise Error

# reading config        
_read_config()

class Selector:
    '''
    iz class for selenium selectors
    '''
    def __init__(self, method: By, statement: str):        
        self.method = method
        self.statement = statement

    def Get(self):
        return (self.method, self.statement)

    def __str__(self):
        return "{ method: " + self.method + ", statement: \"" + self.statement + "\"}"


#region Web-Driver


driver_options = {
    "chrome": DesiredCapabilities.CHROME  #TODO: more browsers
}



def set_webdriver_url(url):
    raise NotImplementedError


def get_webdriver_url():    
    return this._webdriver_url    
    

this.drivers = {}


def GetDriver(driver_alias, browser="chrome"):
    """
    get instance of izWebDriver. available browsers:'chrome' [default: chrome]
    """
    try:
        return this.drivers[driver_alias]
    except KeyError:
        pass
    driver_url = get_webdriver_url()
    if len(this.drivers.keys()) > 9:
        raise Exception("TooManyDriversError: izSelenium contain 10 active drivers")
    
    new_driver = izWebDriver(driver_url, driver_options[browser])
    new_driver.implicitly_wait(TM._implicit_wait)
    if not this.debug_mode:
        save_session(driver_alias, new_driver.session_id) #TODO add try-catch. not saving shouldnt crash 
    this.drivers[driver_alias] = new_driver

    return new_driver


def Quit_All():
    for driver in this.drivers.values():
        driver.quit()
    this.drivers = {}


class izWebDriver(webdriver.Remote):
    """
    iz implementation for selenium web-driver
    """
    def __init__(self, url, capabilities):
        super().__init__(url, capabilities)

    @staticmethod
    def close_open_sessions():
        """
        close all webdriver sessions in webdriver_url.
        """
        if this.debug_mode:            
            log.warn('load_open_session: debug mode on. no session saving')
        else:
            close_open_sessions(get_webdriver_url(), izWebDriver,
                                DesiredCapabilities.CHROME)
    
    @staticmethod
    def load_open_session():
        """
        loads open sessions. returns the sessions.
        after running this function, sessions will allso
        be avialbe via GetDriver method
        """
        if this.debug_mode:                      
            log.warn('load_open_session: debug mode on. no session saving')
        else:
            open_drivers = get_open_sessions(get_webdriver_url(), izWebDriver,
                                             DesiredCapabilities.CHROME)[0]
            this.drivers.update(open_drivers)
            return open_drivers
        return None

    
    def _find(self, selector: Selector, sensitive, root=None):
        """
        internal use only
        """
        log.info("finding " + str(selector))
        if (root):
            findfunction = root
        else:
            findfunction = self.find_element
        # func =   findFunctions[selector.method]
        element = actionWrapper(findfunction, None, [self.accept_alert],
                                "find element failed. ", selector.method,
                                selector.statement)
        if element:
            log.success("find - success")
            if (type(element) is list):
                return izWebElement.ConvertList(element, selector, self)
            else:
                return izWebElement(element, selector, self)
        else:
            if sensitive:
                raise AssertionError("find - failed: [{}].".format(selector.statement))
            else:
                pass    

    def find(self, selector: Selector, sensitive=True):
        """
        finds the first element according to given selector. returns izWebElement
        """
        # driver = this.GetDriver()
        # findFunctions = {
        #     "xpath": driver.find_element_by_xpath,
        #     "css": driver.find_element_by_css_selector
        # }
        return self._find(selector, sensitive=sensitive)

    def finds(self, selector: Selector, sensitive=True):
        """
        finds the all elements according to given selector. returns a list
        """
        # driver = this.GetDriver()
        # findFunctions = {
        #     "xpath": driver.find_element_by_xpath,
        #     "css": driver.find_element_by_css_selector
        # }
        return self._find(
            selector, sensitive=sensitive, root=self._stpd_find_elements)

    def _stpd_find_elements(self, by: By, statement: str):
        lst = self.find_elements(by, statement)
        if lst:
            return lst
        else:
            raise NoSuchElementException()

    def accept_alert(self):
        alert = self.switch_to.alert
        alert.accept()



#endregion

#region web - element

from selenium.webdriver.support.ui import WebDriverWait
class izWebElement(webelement.WebElement):
    """
    iz class for selenium web-element
    """

    def __init__(self, element: webelement.WebElement, selector: Selector, driver:izWebDriver):
        super().__init__(element._parent, element._id)
        self._id = element._id
        self.selector = selector
        self.driver = driver

    def RunJS(self, script, failMassage, sensitive=False):
        """
        iz function - running javascript with the element as arguments[0]
        """
        print("RunJS:" + script)
        try:

            self.driver.execute_script(script, self)
        except Exception as e:
            if sensitive:
                raise e
            else:
                log.fail(self.selector.statement + failMassage)
                log.info("   " + str(e))

    def set_attribute(self, name, value):        
        """
        set attribute of the element (using js setAttribute function)
        """
        # if value is empty, send a string representaion of an empty string
        value = value if str(value) != '' else '""'
        script = f'arguments[0].setAttribute("{name}", {value})'
        self.RunJS(script, f'set_attribute failed for {name}: {value}')

    def click(self, fix_actions = True):
        if fix_actions:
            fix =  [self.scroll_into_view]
        else:
            fix = []
        actionWrapper(
            action=super().click,
            fix_actions= fix,
            alternate=self.jsClick,
            failTitle=self.selector.statement + ": iz-click failed")

    def double_click(self):
        actionWrapper(
            actions.ActionChains(self.driver).double_click(self).perform,
            None,
            [self.scroll_into_view],
            self.selector.statement + ": iz-dbl-click failed")

    def move_to_me(self):
        """
        moves the mouse to the element's location
        """
        actionWrapper(
            actions.ActionChains(self.driver).move_to_element(self).perform,
            [self.scroll_into_view],
            None,
            self.selector.statement + ": iz-move failed")

    def jsClick(self):
        """
        iz method
        """
        print("clicking " + self.selector.statement)
        self.RunJS("arguments[0].click()", "js click failed")

    def jsDouble_click(self):
        """
        iz method
        """
        print("clicking " + self.selector.statement)
        self.RunJS("arguments[0].click();arguments[0].click();", "js click failed")


    def setValue(self, text):
        """
        iz method
        """
        self.RunJS("arguments[0].value='" + text + "'", self.selector.statement,
                   "set value FAIL")

    def appendValue(self, text):
        """
        iz method
        """
        self.RunJS(
            "arguments[0].value=arguments[0].value+'" + text + "'",
            self.selector.statement + "append value FAIL",
            sensitive=True)

    def send_keys(self, *value):
        """
        iz method. 
        """
        if len(value) > 1:
            alt = None
        else:
            alt = self.appendValue
        actionWrapper(super().send_keys, alt, [self.scroll_into_view],
                      self.selector.statement + ": send keys failed", *value)

    def send_keys_noJS(self, *value):
        """
        iz method
        """
        actionWrapper(super().send_keys, None, [self.scroll_into_view],
                      self.selector.statement + ": send keys failed", *value)

    def scroll_into_view(self):
        self.RunJS(
            "arguments[0].scrollIntoView();",
            self.selector.statement + "SCROLL FAIL",
            sensitive=True)

    def highlight(self, sleep_and_stop=2):
        """
        turn current element's border into solid red 2px.
        return original style after 'sleep_and_stop' seconds of time.sleep
        if 'sleep_and_stop' is 0 - border stays and no sleep.        
        original stlyle saved to self.original_style
        """
        self.original_style = self.get_attribute('style')        
        self.set_attribute('style', '"border: 2px solid red;"')
        if sleep_and_stop > 0:
            sleep(sleep_and_stop)
            self.set_attribute('style', self.original_style)        
            
        

        

    def find(self, selector: Selector, sensitive=True):
        """
        finds an element under current element (using current as root)
        """
        return self.driver._find(selector, root=super().find_element, sensitive=sensitive)

    def waitNexist(self):
        from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, ElementNotVisibleException
        timeouts = TM.Get()
        sleep_time = timeouts[1]
        total = 0
        attempt = 0
        timeout = 15
        while (total < timeout):
            try:
                if ((super().is_displayed() or super().rect)):
                    sleep(sleep_time)
                    total += (sleep_time + TM._implicit_wait)
                else:
                    print("WaitNExist success - element not on screen")
                    return True
            except StaleElementReferenceException as e:
                print("WaitNExist success - element is stale")
                return True
            except NoSuchElementException as e:
                print("WaitNExist success - no such element")
                return True
            except ElementNotVisibleException:
                print("WaitNExist success - element not visible")  # in future, return 0,1,2  - fail sucess unvisible ( not visible != not exist)
                return True
            except:
                print("WaitNExist propably success - unknown error")
                return True
            finally:
                attempt += 1
        print("WaitNExist fail - element still here after " + str(total) +
              "seconds")
        return False

    def waitForText(self, text: str, contains=True, sensitive=False):
        """
        wait for this element to display the given text.(using find() every time)
        contains - it's enough that the element will *contain* the text
        """
        try:
            return actionWrapper(
                _ar_compare_text, [self.scroll_into_view], None,
                self.selector.statement + " text " + text + " hasn't showed",
                self, text, contains, sensitive)
        except Exception as e:
            if sensitive:
                raise e
            return False

    @staticmethod
    def ConvertList(lst: list, selector, driver):
        """
        convert a list of classic webelements to izWebElelemnts
        """
        newLst = []
        for e in lst:
            newLst.append(izWebElement(e, selector, driver))
        return newLst

    def get_text(self):
        """
        get text of current element using either 'text' or 'innerHTML' attributes
        """
        from selenium.common.exceptions import StaleElementReferenceException
        for i in range(0,2):
            try:
                if (super().text):
                    return super().text
                elif (super().get_attribute('innerHTML')):
                    return (super().get_attribute('innerHTML'))
            except StaleElementReferenceException:  # this approch can be usfull at more places
                log.info("iz.get_text: re-finding stale element "+self.selector.statement)
                self = self.driver.find(self.selector)
        return None

    def move_element_by_offset(self, x, y):
        """
        moves the element by offset of x and y.
        """
        actionWrapper(
            actions.ActionChains(self.driver).drag_and_drop_by_offset(
                self, x, y).perform, [self.scroll_into_view], None,
            self.selector.statement + ": iz-move failed")

# TODO possibly deprecate:
# def _ar_compare_text(element: izWebElement, text: str, contains, throw_msg=""):
#     result = self.webdiver.find(element.selector.method,
#                   element.selector.statement).get_text()
#     if (contains and text in result) or text == result:
#         return True
#     raise Exception(throw_msg)

# endregion



