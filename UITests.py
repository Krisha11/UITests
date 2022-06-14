import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from webdriver_manager.firefox import GeckoDriverManager

class TestUI:
    def setup_class(self):
        self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
        self.wait = WebDriverWait(self.driver, 2)

    @pytest.fixture(autouse=True)
    def driver_starting(self):
        self.driver.get('https://bb.spbu.ru/')
        yield

    def teardown_class(self):
        self.driver.close()

    def auth(self) :
        self.driver.find_element(By.ID, 'user_id').send_keys(os.getenv('LOGIN'))
        self.driver.find_element(By.ID, 'password').send_keys(os.getenv('PASSWORD') + Keys.RETURN)
        self.driver.save_screenshot("auth.jpg")

    def get_by_xpath(self, xpath) :
        return self.driver.find_element(By.XPATH, xpath)

    def go_to_community_page(self) :
        self.driver.find_element(By.ID, 'Community.label').click()
        sleep(1)
    
    def go_to_main_page(self) :
        self.driver.get('https://bb.spbu.ru/')
        sleep(3)

    def test_auth(self) :
        self.auth()
        sleep(5) # очень медленный сайт, нужно ждать прогрузки 

        # проверка url, для того чтобы удостовериться в успешности авторизации
        self.driver.save_screenshot("main.jpg")
        assert self.driver.current_url == 'https://bb.spbu.ru/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_1_1'

    def test_fake_search_community(self):
        self.go_to_main_page()
        self.go_to_community_page()
        self.driver.find_element(By.ID, 'courseSearchText').send_keys('bla bla bla' + Keys.RETURN)
        sleep(3)
    
        self.driver.save_screenshot("fake_search.jpg")
        assert self.get_by_xpath('//*[@id="containerdiv"]').text == "Не обнаружены организации, соответствующие критериям поиска."

    def test_normal_search_community(self) :
        self.go_to_main_page()
        self.go_to_community_page()
        self.driver.find_element(By.ID, 'courseSearchText').send_keys('Бакалавриат' + Keys.RETURN)
        sleep(3)

        self.driver.save_screenshot("ok_search.jpg")
        assert self.get_by_xpath('//*[@id="containerdiv"]').text != "Не обнаружены организации, соответствующие критериям поиска."

    def test_simple_calendar_checks(self) :
        self.go_to_main_page()
        self.driver.find_element(By.LINK_TEXT, 'Календарь').click()
        sleep(3)

        self.driver.save_screenshot("calendar.jpg")
        assert self.driver.current_url == 'https://bb.spbu.ru/webapps/calendar/viewPersonal'
        assert self.get_by_xpath('/html/body/div[6]/div[2]/div/div/div/div/div/div[1]/h1/span[2]').text == 'Календарь'

    def test_inaccessibility_of_prohibited_objects(self) :
        for name in ['Бакалавриат и специалитет.', 'Магистратура.', 'Аспирантура.'] :
            self.go_to_main_page()
            self.driver.find_element(By.LINK_TEXT, name).click()
            sleep(3)

            self.driver.save_screenshot("prohibited_" + name + ".jpg")
            assert self.get_by_xpath('/html/body/div[6]/div/div/div/div[1]/div/h1/span/span').text == 'Гостям не разрешен переход на этот курс.'
            assert self.get_by_xpath('//*[@id="bbNG.receiptTag.content"]').text == 'Гостям не разрешен переход на этот курс.'

    def test_ability_to_check_browser(self):
        self.go_to_main_page()

        self.driver.save_screenshot("ability_to_check_browser.jpg")
        assert self.get_by_xpath('/html/body/div[6]/div/div/div[2]/div[2]/div/div/div/div[1]/div/div/p').text \
                == 'Нажмите эту кнопку, чтобы проверить - настроен ли Ваш браузер для работы в Blackboard?     --    Use the button below to check if your web browser is properly configured to use Blackboard'
