from izSelenium import get_driver, By, Selector

s_inpt = Selector(By.CSS_SELECTOR, ".new-todo")

d = get_driver('bb')
d.get("http://todomvc.com/examples/react/#/")
inpt = d.find(s_inpt)

inpt.send_keys('hello world')

print("hi")