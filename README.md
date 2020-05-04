# Autotet.Web
selenium based infrastructure for web automation tests

## basic usage
```python

from Autotest.izSelenium import get_driver, Selector, By

# get izWebdriver
driver = get_driver('google') # now izSelenium saved a driver instance with an alias 'google'
gmail_driver = get_driver('gmail-driver') # this is another driver session: another window. 


# to seperate logic from html, we use an object called 'selector' to select elements on a web page. 
s_search_input = Selector(By.CSS_SELECTOR, f"form input[title='{SEARCH_TITLE}']")

# it's recomended to actually search for elements in a dedicated function
def search_input():
    return driver.find(s_search_input)

# izWebDriver has all webdriver functions and some more
keep_driver.get(KEEP_URL)

driver.get(r"http://www.google.com")
# izSelenium actions, like following 'send_keys', use restries and fix-actions - such as trying to set value with JS in case of failure
search_input().send_keys("i know how to automate") 

```
