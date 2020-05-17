__doc__ = "selectors for chrome stettings and menu"
from izSelenium import Selector, By
driver  = None

URL_SETTINGS = "chrome://settings/"

s_lbl_advanced = Selector(By.CSS_SELECTOR,"#advanced-settings-expander")
def lblAdvanced():
    return driver.find(s_lbl_advanced)

s_btn_privacy = Selector(By.CSS_SELECTOR,"#privacyContentSettingsButton")
def btnPrivacy(sensitive = True):
    return driver.find(s_btn_privacy, sensitive)

s_btn_popup_exceptions  = Selector(By.XPATH, "//button[@contenttype='plugins']")
def btnPopupException():
    return driver.find(s_btn_popup_exceptions)

s_inpt_hostname = Selector(By.XPATH, "//*[@id='content-settings-exceptions-area']/div[2]/div[5]/list/div[2]/div/div/input")

def inptHostname():
    return driver.find(s_inpt_hostname)

s_btn_confirm_exception = Selector(By.CSS_SELECTOR, "#content-settings-exceptions-overlay-confirm")
def btnConfirmException():
    return driver.find(s_btn_confirm_exception)

s_btn_confirm_settings = Selector(By.CSS_SELECTOR, "#content-settings-overlay-confirm")
def btnConfirmSettings():
    return driver.find(s_btn_confirm_settings)

s_add_exc_form = Selector(By.CSS_SELECTOR, '#exception-column-headers')
def frmAdd_exc():
   return driver.find(s_add_exc_form)

_txt_added =  "//div[@class='static-text' and contains(text(),'$$')]"
def txtAdded(text:str):
    return driver.find(Selector(By.XPATH, _txt_added.replace('$$',text)), sensitive=False)
