import time
import unittest
from selenium import webdriver
import HtmlTestRunner
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys


class FrontendTestCase(unittest.TestCase):
    options = webdriver.ChromeOptions()
    service = ChromeService("C:\\Users\\User\\CS308_TasteTwister-2\\backend\\drivers\\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)

    def test_a_login(self):
        self.driver.implicitly_wait(3)
        self.driver.get("http://localhost:3000/")
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)

        self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div/form/div[1]/input').send_keys("betul")
        self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div/form/div[2]/input').send_keys("passvoid")
        self.driver.implicitly_wait(10)
        time.sleep(5)
        self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div/form/button').click()
        time.sleep(5)
        self.driver.implicitly_wait(10)
        self.assertEqual("http://localhost:3000/home", self.driver.current_url)

    def test_b_playlist_import(self):
        self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/button[1]').click()
        self.driver.implicitly_wait(10)
        self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div[3]/input').send_keys("https://open.spotify.com/playlist/1zKMzjGfozCdFrJPrpIXSw?si=fb9b837a9dd6470b")
        self.driver.implicitly_wait(10)
        self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div[3]/button[2]').click()
        self.driver.implicitly_wait(10)
        time.sleep(5)
        alert = self.driver.switch_to.alert
        self.driver.implicitly_wait(10)
        time.sleep(5)
        alert_text = alert.text
        self.driver.implicitly_wait(10)
        time.sleep(5)
        alert.accept()
        self.driver.implicitly_wait(10)
        time.sleep(5)
        self.assertEqual('The Spotify playlist is imported successfully!', alert_text)

    def test_c_logout(self):
        self.driver.find_element(By.CLASS_NAME, 'logout-button').click(),
        self.driver.implicitly_wait(10)
        self.assertEqual("http://localhost:3000/", self.driver.current_url)

if __name__ == '__main__':
    unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output='C:\\Users\\User\\CS308_TasteTwister-2\\backend\\reports'),verbosity=2)
