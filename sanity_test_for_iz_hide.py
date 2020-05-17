from izSelenium import get_driver, By, Selector

s_inpt = Selector(By.XPATH, "//section//li//label[text()='hello']/../input[@type='checkbox']")

d = get_driver('bb')
d.get("http://todomvc.com/examples/react/#/")
inpt = d.find(s_inpt)

boolean_value = inpt.is_selected()
print("hi")