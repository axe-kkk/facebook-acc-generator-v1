import os
import requests
import random
import time
from stem import Signal
from stem.control import Controller
from stem import SocketError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from fake_useragent import UserAgent
import secrets
import string
from datetime import datetime
from selenium.webdriver.common.proxy import Proxy, ProxyType


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


def renew_tor_ip():
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
            print("<LOG> IP обновлен успешно.")
    except SocketError as e:
        print("<LOG> Не удалось подключиться к контроллеру Tor.", '\n<ERROR>', e)
    except Exception as e:
        print("<LOG> Ошибка при попытке обновить IP.", '\н<ERROR>', e)


def test_tor_connection():
    try:
        proxies = {
            'http': 'socks5://127.0.0.1:9050',
            'https': 'socks5://127.0.0.1:9050'
        }
        print("Текущий IP:", requests.get('https://ident.me', proxies=proxies).text)
    except Exception as e:
        print('<LOG> Tor не подключен. Проверьте свое соединение с Tor', '\n<ERROR>', e)


def get_verification_code(email):
    login, domain = email.split('@')
    for _ in range(10):
        response = requests.get(f'https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}')
        messages = response.json()
        if messages:
            message_id = messages[0]['id']
            message_response = requests.get(f'https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={message_id}')
            message_body = message_response.json()
            return message_body['body'].split('is: ')[1].split('<')[0]
        time.sleep(5)
    return None


def register_account():
    first_name, last_name, gender, password, date = get_fake_person_data()
    email = get_temp_email()
    user_agent = UserAgent()
    renew_tor_ip()

    options = FirefoxOptions()
    options.headless = True
    options.add_argument(f'user-agent={user_agent.random}')
    proxy = Proxy({
        'proxyType': ProxyType.MANUAL,
        'httpProxy': '127.0.0.1:9050',
        'sslProxy': '127.0.0.1:9050',
        'socksProxy': '127.0.0.1:9050'
    })

    service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options, proxy=proxy)
    driver.get("https://www.facebook.com/")

    screenshot_dir = 'screenshots'
    os.makedirs(screenshot_dir, exist_ok=True)

    # Принятие cookies
    try:
        accept_button = driver.find_element(By.CSS_SELECTOR, 'button[data-cookiebanner="accept_button"], button[title="Allow all cookies"]')
        accept_button.click()
    except Exception as e:
        print('<LOG> Не удалось найти кнопку принятия cookies.', '\n<ERROR>', e)
        driver.save_screenshot(os.path.join(screenshot_dir, 'cookie_error_screenshot.png'))
        driver.quit()
        return None

    # Нажать на кнопку "Get started"
    try:
        get_started_button = driver.find_element(By.XPATH, '//a[text()="Create new account"]')
        get_started_button.click()
    except Exception as e:
        print('<LOG> Не удалось найти кнопку "Create new account".', '\n<ERROR>', e)
        driver.save_screenshot(os.path.join(screenshot_dir, 'error_screenshot.png'))
        driver.quit()
        return None

    # Заполнение формы регистрации
    try:
        driver.find_element(By.NAME, 'firstname').send_keys(first_name)
        driver.find_element(By.NAME, 'lastname').send_keys(last_name)
        driver.find_element(By.NAME, 'reg_email__').send_keys(email)
        driver.find_element(By.NAME, 'reg_passwd__').send_keys(password)

        driver.find_element(By.NAME, 'birthday_day').send_keys(str(date[2]))
        driver.find_element(By.NAME, 'birthday_month').send_keys(str(date[1]))
        driver.find_element(By.NAME, 'birthday_year').send_keys(str(date[0]))

        driver.find_element(By.NAME, 'reg_email_confirmation__').send_keys(email)

        if gender == 'male':
            driver.find_element(By.CSS_SELECTOR, 'input[value="2"][name="sex"]').click()
        else:
            driver.find_element(By.CSS_SELECTOR, 'input[value="1"][name="sex"]').click()

        driver.find_element(By.NAME, 'websubmit').click()
    except Exception as e:
        print('<LOG> Не удалось заполнить форму регистрации.', '\n<ERROR>', e)
        driver.save_screenshot(os.path.join(screenshot_dir, 'fill_form_error_screenshot.png'))
        driver.quit()
        return None

    try:
        driver.implicitly_wait(60)
        driver.get('https://www.facebook.com/confirmemail.php?next=*')
    except Exception as e:
        print('<LOG> Не удалось перейти на страницу подтверждения.', '\n<ERROR>', e)
        driver.save_screenshot(os.path.join(screenshot_dir, 'confirmation_error_screenshot.png'))
        driver.quit()
        return None

    verification_code = get_verification_code(email)
    if verification_code:
        driver.find_element(By.NAME, 'code').send_keys(verification_code)
        driver.find_element(By.NAME, 'confirm').click()
    else:
        print("<LOG> Не удалось получить код подтверждения.")

    driver.quit()

    return {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password": password
}


def register_multiple_accounts(count):
    accounts = []
    for _ in range(count):
        account = register_account()
        if account:
            accounts.append(account)
    return accounts


accounts = register_multiple_accounts(1)
print(accounts)
