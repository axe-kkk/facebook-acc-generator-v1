import requests
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import secrets
import string
from datetime import datetime
import time
from webdriver_manager.chrome import ChromeDriverManager
import logging
from stem import Signal
from stem.control import Controller

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_temp_email():
    response = requests.get('https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1')
    return response.json()[0]


def get_fake_person_data():
    response = requests.get('https://randomuser.me/api/')
    person_data = response.json()
    first_name = person_data['results'][0]['name']['first']
    last_name = person_data['results'][0]['name']['last']
    gender = person_data['results'][0]['gender']
    letters = string.ascii_letters
    digits = string.digits
    selection_list = letters + digits
    password_len = 10
    password = ''.join(secrets.choice(selection_list) for i in range(password_len))
    date = person_data['results'][0]['dob']['date']
    date_of_birth = datetime.fromisoformat(date.rstrip('Z'))
    date_array = [date_of_birth.year, date_of_birth.month, date_of_birth.day]
    return first_name, last_name, gender, password, date_array


def get_verification_code(email):
    login, domain = email.split('@')
    while True:
        response = requests.get(f'https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}')
        messages = response.json()
        if messages:
            return messages[0]['subject'].split(" ")[0]
        print("Письмо не найдено, перепроверка через 5 секунд...")
        time.sleep(5)


def random_time_waiting():
    return random.uniform(2, 4)


def renew_tor_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
        time.sleep(10)  # Подождите некоторое время, чтобы IP-адрес обновился


def paused_input(driver, selectror, input_data):
    for i in input_data:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, selectror))).send_keys(
            i)


def register_account():
    first_name, last_name, gender, password, date = get_fake_person_data()
    email = get_temp_email()
    user_agent = UserAgent(platforms="mobile").random
    chrome_options = Options()
    chrome_options.add_argument(f"user-agent={user_agent}")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Настройки прокси для Tor
    chrome_options.add_argument('--proxy-server=socks5://127.0.0.1:9050')

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    try:

        driver.get("https://www.facebook.com/")
        time.sleep(5)
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                    'button[type="submit"]._54k8._52jh._al65'))).click()
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'span[data-bloks-name="bk.components.TextSpan"]'))).click()
        time.sleep(random_time_waiting())
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                    'div[data-bloks-name="bk.components.Flexbox"][tabindex="0"][role="checkbox"][aria-checked="false"][aria-label="English (US)"]'))).click()
        time.sleep(random_time_waiting())
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                    'div[data-bloks-name="bk.components.Flexbox"][tabindex="0"][role="button"][aria-label="Create new account"][data-anchor-id="replay"]'))).click()
        time.sleep(random_time_waiting())
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                    'div[data-bloks-name="bk.components.Flexbox"][tabindex="0"][role="button"][aria-label="Get started"]'))).click()
        time.sleep(random_time_waiting())
        paused_input(driver, 'input[data-bloks-name="bk.components.TextInput"][aria-label="First name"]', first_name)

        time.sleep(random_time_waiting())
        paused_input(driver, 'input[data-bloks-name="bk.components.TextInput"][aria-label="Last name"]', last_name)

        time.sleep(random_time_waiting())
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                    'div[data-bloks-name="bk.components.Flexbox"][tabindex="0"][role="button"][aria-label="Next"]'))).click()
        time.sleep(random_time_waiting())
        birth_date = f"{date[2]:04d}-{date[1]:02d}-{date[0]:02d}"
        print(birth_date)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                    'input[data-bloks-name="bk.components.TextInput"][aria-label="Birthday (0 year old)"]'))).send_keys(
            birth_date)
        time.sleep(random_time_waiting())
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                    'div[data-bloks-name="bk.components.Flexbox"][tabindex="0"][role="button"][aria-label="Next"]'))).click()
        time.sleep(random_time_waiting())
        if gender == 'male':
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Male']"))).click()
        else:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Female']"))).click()
        time.sleep(random_time_waiting())
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Next']"))).click()
        time.sleep(random_time_waiting())
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                    'div[data-bloks-name="bk.components.Flexbox"][tabindex="0"][role="button"][aria-label="Sign up with email"]'))).click()
        time.sleep(random_time_waiting())
        paused_input(driver, 'input[data-bloks-name="bk.components.TextInput"][aria-label="Email"]', email)

        time.sleep(random_time_waiting())
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Next']"))).click()
        time.sleep(random_time_waiting())
        paused_input(driver, 'input[data-bloks-name="bk.components.TextInput"][aria-label="Password"]', password)

        time.sleep(random_time_waiting())
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Next']"))).click()
        time.sleep(random_time_waiting())
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Save']"))).click()
        time.sleep(random_time_waiting())
        WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='I agree']"))).click()
        time.sleep(60)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                    'input[data-bloks-name="bk.components.TextInput"][aria-label="Confirmation code"]'))).send_keys(
            get_verification_code(email))
        time.sleep(10)
        time.sleep(random_time_waiting())
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Next']"))).click()
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
    finally:
        driver.quit()

    return {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password": password,
        "user_agent": user_agent
    }


def register_multiple_accounts(count):
    accounts = []
    for _ in range(count):
        renew_tor_ip()
        account = register_account()
        accounts.append(account)
    return accounts


if __name__ == '__main__':
    proxies = {
        'http': 'socks5://127.0.0.1:9050',
        'https': 'socks5://127.0.0.1:9050'
    }

    print("<LOG> Your IP - ", requests.get('https://ident.me', proxies=proxies).text)
    print()
    print(register_account())
