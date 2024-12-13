import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, InvalidSelectorException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent

from config import settings

logger = logging.getLogger(__name__)


class SeleniumDriver:

    def __init__(self):
        options = webdriver.ChromeOptions()

        useragent = UserAgent()

        while "Windows" not in (user_agent := useragent.random):
            continue

        options.add_argument(f"user-agent={user_agent}")

        for argument in settings.arguments:
            options.add_argument(argument)

        self.driver = webdriver.Chrome(
            options=options
        )

        self.wait = WebDriverWait(self.driver, 10)


class BelurkManager(SeleniumDriver):

    def __init__(self):
        super().__init__()

        self.result = []

    def run(self):

        """
            Authenticates user with given credentials
            and fetches remaining proxy lifetime from personal account page

            Returns:
                Prints out program's result in console

            Raises:
                ValueError: if attempted to log in with incorrect credentials
                RuntimeError: if exceeds login limit attempts
                TimeoutException: if the element is not detected
                InvalidSelectorException: if element's selector name is invalid
        """

        logger.info("Starting program")
        try:
            logger.info("Opening resource")
            self.driver.get("https://belurk.online/")
            logger.info("Resource opened")
            self.__main_page()

        except ValueError:
            logger.error("Incorrect credentials in login data")

        except RuntimeError:
            logger.error("Login limit's exceeded")

        except TimeoutException as ex:
            logger.error(f"Can't find the element {ex.msg}")

        except InvalidSelectorException as ex:
            logger.error(f"Can't find the element by selector: {ex.msg}")

        finally:
            logger.info("Finishing program")
            self.driver.quit()

            return print(''.join([*self.result])) if self.result else None

    def __get_element_by_css_selector(self, css_selector: str):
        return self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )

    def __main_page(self):
        logger.info("Getting login button")
        login_button = self.__get_element_by_css_selector("a.font-semibold:nth-child(1)")
        logger.info("Login button selected")
        login_button.click()

        logger.info("Forwarding to login page")
        self.__login_page()

    def __login_page(self):
        login_data = {"Login": settings.login, "Password": settings.password}
        for i, (k, v) in enumerate(login_data.items()):
            logger.info(f"Inserting {k} data")
            data_input = self.__get_element_by_css_selector(
                f"div.w-full:nth-child({i+1}) > div:nth-child(1) > input:nth-child(1)"
            )
            data_input.send_keys(v)
            logger.info(f"{k} data inserted")

        logger.info("Getting login form button")
        form_button = self.__get_element_by_css_selector("button.w-full")
        logger.info("Login form button selected")

        logger.info("Submitting login form")
        login_url = self.driver.current_url
        time.sleep(1)
        form_button.click()
        time.sleep(3)

        if self.driver.current_url == login_url:
            login_error = self.wait.until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    ".ml-\[20px\]"
                ))
            ).text

            if login_error in ['Неверный логин или пароль', "Неверный email", "Пароль должен быть не менее 6 символов"]:
                raise ValueError
            elif login_error == 'Превышен лимит попыток регистрации':
                raise RuntimeError

        logger.info("Forwarding to personal account page")
        self.__personal_account_page()

    def __personal_account_page(self):
        logger.info("Getting ipv4_sheet")
        ipv4_page = self.__get_element_by_css_selector("a.px-\[25px\]:nth-child(3)")
        logger.info("ipv4_sheet selected")
        logger.info("Opening ipv4_sheet")
        ipv4_page.click()
        logger.info("ipv4_sheet opened")

        logger.info("Waiting till the last row in the table is loaded")
        self.__get_element_by_css_selector("tr.group:nth-child(2)")
        logger.info("Last row has loaded")

        logger.info("Getting number of rows in the table")
        rows = self.driver.find_elements(By.TAG_NAME, "tr")
        logger.info("Number of rows has received")

        logger.info("Getting wanted data")
        for i in range(1, len(rows)):
            row = rows[i].text.split("\n")
            ip_column, expire_column = row[4], row[8]
            self.result.append(f"{ip_column} - {expire_column}\n")
        logger.info("Wanted data collected")
