# Autotet.Web
selenium based infrastructure for web automation tests

## basic usage
```python

from izSelenium import GetDriver

# get izWebdriver
keep_driver = GetDriver('keep') # that's it. you have a working chrome-driver
gmail_driver = GetDriver('gmail-driver') # this is another driver session: another window

# izWebDriver has all webdriver functions and some more
keep_driver.get(KEEP_URL)

# in izSelenium we find elements with 'Selectors' as defined in izSelenium.Selector
iz_element = keep_driver.find(NEW_NOTE_SELECTOR)
# izWebElement has all webdriver functions and some more
iz_element.click()
iz_element.set_value('this value just appears using JS value attribute')
keep_driver.find(CLOSE_BTN_SELECTOR).click()

gmail_driver.get(GMAIL_URL)
check_for_reminder_from_keep(gmail_driver)

```