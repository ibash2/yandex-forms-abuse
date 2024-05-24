import functools
import json
import time
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from random import randint
from multiprocessing import Pool


class YandexFormFiller:
    def __init__(self, cookies_file_path, captcha_cookies_file_path, form_url):
        self.cookies_file_path = cookies_file_path
        self.captcha_cookies_file_path = captcha_cookies_file_path
        self.form_url = form_url
        self.driver = self._initialize_driver()

    def _initialize_driver(self):
        ua = UserAgent()
        options = Options()
        # options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"user-agent={ua.chrome}")
        options.add_extension("block.crx")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        return driver

    def load_cookies(self, path):
        with open(path, "r") as cookies_file:
            cookies = json.load(cookies_file)
            for cookie in cookies:
                self.driver.add_cookie(cookie)

    def save_cookies(self, path):
        cookies = self.driver.get_cookies()
        with open(path, "w") as file:
            json.dump(cookies, file)

    def handle_captcha(self):
        while "https://forms.yandex.ru/showcaptcha" in self.driver.current_url:
            self.load_cookies(self.captcha_cookies_file_path)
            time.sleep(5)
            self.save_cookies(self.captcha_cookies_file_path)

    def fill_form(self):
        self.driver.get(self.form_url)
        self.load_cookies(self.cookies_file_path)
        self.handle_captcha()
        time.sleep(2)

        checkbox_elements = self.driver.find_elements(
            by=By.CLASS_NAME,
            value="CheckboxQuestion-Control",
        )

        for checkbox in checkbox_elements:
            options = checkbox.find_elements(by=By.TAG_NAME, value="label")
            selected_option = randint(0, len(options) - 1)
            options[selected_option].click()
            time.sleep(randint(1, 2))
            print(options[selected_option].text)

        self.driver.find_element(by=By.CSS_SELECTOR, value="button.g-button").click()

    def close(self):
        self.save_cookies(self.cookies_file_path)
        self.driver.close()


# Usage example
if __name__ == "__main__":
    with Pool() as p:
        form_filler = YandexFormFiller(
            "cookies.json",
            "captcha_cookies.json",
            "https://forms.yandex.ru/u/{id}/",
        )
        form_filler.fill_form()
        form_filler.close()

        processes = [
            p.apply_async(functools.partial(form_filler.fill_form)) for _ in range(6)
        ]
        print(f"Process: {len(processes)}")

        for process in processes:
            process.get()
