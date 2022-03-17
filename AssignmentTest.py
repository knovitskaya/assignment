from selenium import webdriver
import json
import unittest
from selenium.webdriver.support.ui import Select
from datetime import datetime
import time

class TestStringMethods(unittest.TestCase):
    def setUp(self):
        f = open('config.json')
        data = json.load(f)

        self.Language = data['Language']
        self.Country = data['Country']

        self.driver = webdriver.Chrome('/Users/Katerina/Downloads/chromedriver')

        self.driver.implicitly_wait(120)
        self.driver.maximize_window()

    def test_login(self):
        self.driver.get("https://www.libreview.com/")
        select_country = Select(self.driver.find_element_by_xpath("//select[@name='country']"))
        select_country.select_by_visible_text(self.Country)
        select_language = Select(self.driver.find_element_by_xpath("//select[@name='language']"))
        select_language.select_by_visible_text(self.Language)
        self.driver.find_element_by_xpath("//button[@id='submit-button']").click()

        self.driver.find_element_by_xpath("//input[@name='email']").send_keys("codechallengeadc@outlook.com")
        self.driver.find_element_by_xpath("//input[@name='password']").send_keys("P@ssword$12")
        self.driver.find_element_by_xpath("//button[@id='loginForm-submit-button']").click()
        self.driver.find_element_by_xpath("//button[@id='twoFactor-step1-next-button']").click()

        # get time of when 2FA was requested
        before2fa = datetime.today()
        # since seconds are not reported on outlook ui, set seconds to zero
        before2fa = before2fa.replace(second=0, microsecond=0)
        # open new tab and switch to it

        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])

        self.driver.get("https://login.live.com/")

        self.driver.find_element_by_xpath("//input[@type='email']").send_keys("codechallengeadc@outlook.com")
        self.driver.find_element_by_xpath("//input[@type='submit']").click()
        time.sleep(2)
        self.driver.find_element_by_xpath("//input[@type='password']").send_keys("P@ssword$1234")
        self.driver.find_element_by_xpath("//input[@type='submit']").click()
        self.driver.find_element_by_xpath("//input[@value='No']").click()

        self.driver.get("https://outlook.live.com/mail/0/")

        # wait for the e-mail to arrive by checking the timestamp
        # if in 100 seconds validation e-mail does not arrive, assert
        timeout = 10
        while timeout > 0:
            self.driver.find_element_by_xpath("//span[text()='LibreView Verification Code']").click()
            mail_date_text = self.driver.find_element_by_xpath("//span[@aria-label='Opens Profile Card for LibreView']/../../div/div/div[2]").text
            mail_date = datetime.strptime(mail_date_text, '%a %m/%d/%Y %I:%M %p')
            if before2fa <= mail_date:
                break
            timeout = timeout - 1
            time.sleep(10)
            self.driver.refresh()

        assert timeout > 0, "Error: validation code never arrived."
        validation_code = self.driver.find_element_by_xpath("//td[contains(text(),'Your security code is:')]").text
        validation_code = validation_code.split(": ")[1].strip()
        # close e-mail window
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.driver.find_element_by_xpath("//input[@name='code2fa']").send_keys(validation_code)
        self.driver.find_element_by_xpath("//button[@id='twoFactor-step2-next-button']").click()
        upload_button = self.driver.find_elements_by_xpath("//button[@id='meterUpload-linkedUpload-pat-button']")
        assert len(upload_button) > 0, "Error Press to Begin Upload button is not found after login."

if __name__ == '__main__':
    unittest.main()





















