import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select

class DEMO_():
    def demo(self):
        driver = webdriver.Chrome(options=Options())
        wait = WebDriverWait(driver, 15)
        
        driver.get("https://www.saucedemo.com/")
        # driver.find_element(By.CLASS_NAME,"style_input__KIaTp").send_keys("inder@test.com")
        driver.find_element(By.XPATH,'//input[@placeholder="Username"]').send_keys("standard_user")
        driver.find_element(By.XPATH,'//input[@placeholder="Password"]').send_keys("secret_sauce")
        driver.find_element(By.XPATH,'//input[@ id="login-button"]').click()
        time.sleep(5)
        driver.quit()
findbyid = DEMO_()
findbyid.demo()
