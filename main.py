import asyncio
from fake_useragent import UserAgent
from random import randint

from playwright.async_api import async_playwright
from playwright.async_api._generated import Playwright


class YandexFormFiller:
    def __init__(
        self,
        playwright: Playwright,
        cookies_file_path,
        captcha_cookies_file_path,
        form_url,
    ):
        self.cookies_file_path = cookies_file_path
        self.captcha_cookies_file_path = captcha_cookies_file_path
        self.form_url = form_url
        self.playwright = playwright

    async def _initialize_driver(self):
        ua = UserAgent()
        browser = await self.playwright.chromium.launch(headless=False)

        context = await browser.new_context(
            storage_state="cookies.json",
            user_agent=ua.chrome,
        )

        driver = await context.new_page()

        return driver

    async def handle_captcha(self):
        while "https://forms.yandex.ru/showcaptcha" in self.driver.url:
            await asyncio.sleep(5)

    async def fill_form(self):
        self.driver = await self._initialize_driver()
        await self.driver.goto(self.form_url)
        await self.handle_captcha()
        await asyncio.sleep(2)

        checkbox_elements = self.driver.locator(
            ".CheckboxQuestion-Control",
        )
        count = await checkbox_elements.count()

        for i in range(count):
            inner_elements = checkbox_elements.nth(i).locator("label")
            inner_elements_count = await inner_elements.count()

            clicked_option = randint(0, inner_elements_count - 1)
            await inner_elements.nth(clicked_option).click()
            text = await inner_elements.nth(clicked_option).text_content()
            await asyncio.sleep(randint(1, 2))

            print(text)

        await self.driver.locator("button.g-button").click()
        await asyncio.sleep(20)

    def close(self):
        self.save_cookies(self.cookies_file_path)
        self.driver.close()


async def main():
    async with async_playwright() as p:
        form_filler = YandexFormFiller(
            p,
            "cookies.json",
            "captcha_cookies.json",
            "https://forms.yandex.ru/u/5eaa7a8b6a56c71326740436/",
        )
        await form_filler.fill_form()


# Usage example
if __name__ == "__main__":
    asyncio.run(main())
