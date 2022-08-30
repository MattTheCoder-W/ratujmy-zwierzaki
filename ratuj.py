from time import sleep
from argparse import ArgumentParser
import concurrent.futures
import colorama
from colorama import Fore, Back, Style
from termcolor import colored

from random import randint
from fake_useragent import UserAgent

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

from datetime import datetime

colorama.init()

SAVED = 0
START = datetime.now()

class Ratownik:
    def __init__(self, obj_id: int, timeout: int = 1, max_timeout: int = 15, intimeout: float = 1.5) -> None:
        self.running = False
        self.ID = obj_id
        self.laps = 0
        self.page_url = "https://whatwevalue.telekom.com/pl-PL/projects/2B7EbLBBdvXrBQsGbhIasl"
        self.cookies_accept_xpath = "/html/body/div/div/div[1]/main/div[1]/div[2]/div/div[2]/div[2]/button[1]"
        self.like_selector = ".boost-us-button"
        self.TIMEOUT = timeout
        self.MAX_TIMEOUT = max_timeout
        self.intimeout = intimeout
        self.driver = self.wait = None
        self.create_browser()

    def create_browser(self) -> None:
        options = Options()
        options.headless = True
        options.add_argument(f'user-agent={UserAgent().random}')

        self.driver = webdriver.Firefox(options=options)
        self.wait = WebDriverWait(self.driver, self.MAX_TIMEOUT)
        print(f"[browser-{self.ID}] Instance recreated!")

    def get_dialog(self, driv) -> list:
        return self.driver.find_elements(By.CSS_SELECTOR, 'vbox.dialogOverlay:nth-child(1) > vbox:nth-child(1) > browser:nth-child(2)')

    def clear_cookies(self) -> None:
        self.driver.get("about:preferences#privacy")
        self.driver.find_elements(By.CSS_SELECTOR, '#clearSiteDataButton')[0].click()

        script = (
            'const browser = document.querySelector("vbox.dialogOverlay:nth-child(1) > vbox:nth-child(1) > browser:nth-child(2)");' +
            'browser.contentDocument.documentElement.querySelector("dialog")._doButtonCommand("accept")'
        )

        self.wait.until(self.get_dialog)
        self.driver.execute_script(script)

        self.wait.until(EC.alert_is_present())
        alert = Alert(self.driver)
        alert.accept()
   
    def get_accept_cookies(self, driv) -> list:
        return self.driver.find_elements(By.XPATH, self.cookies_accept_xpath)

    def save_animal(self) -> None:
        while self.running:
            sleep(0.1)
        while True:
            try:
                self.running = True
                global SAVED
                global START
                prefix = Fore.MAGENTA + Style.BRIGHT + f"[browser-{Fore.RED}{self.ID}{Fore.MAGENTA}, lap={Fore.RED}{self.laps}{Fore.MAGENTA}]" + Style.RESET_ALL
                while True:
                    self.driver.get(self.page_url)
                    sleep(self.intimeout)
                    try:
                        self.wait.until(self.get_accept_cookies)
                        break
                    except TimeoutException:
                        pass
                self.get_accept_cookies(None)[0].click()
                self.driver.execute_script('document.querySelector(".boost-us-button").scrollIntoView();')
                sleep(self.intimeout)
                self.driver.find_elements(By.CSS_SELECTOR, self.like_selector)[0].click()
                self.laps += 1

                print(f"{prefix} -- time {str(datetime.now() - START).split('.')[0]} -- [CPM:{round(SAVED/(datetime.now() - START).total_seconds(),10)*60}] [{SAVED}] " + Fore.GREEN + "Animal saved!" + Style.RESET_ALL)
                SAVED += 1
                self.clear_cookies()
                self.running = False
                print(f"{prefix} " + Fore.YELLOW + "INFO:" + Style.RESET_ALL + f" Cookies cleared, waiting {self.TIMEOUT} seconds before restart")
                sleep(self.TIMEOUT)
            except Exception as e:
                with open("log.log", "a") as f:
                    print(Fore.RED + Style.BRIGHT + "Got Error! Skipping..." + Style.RESET_ALL)
                    f.write(str(type(e)) + str(e) + "\n")
                self.driver.quit()
                self.create_browser()
                continue
            break

    def close(self) -> None:
        self.driver.quit()
        print(Fore.MAGENTA + Style.BRIGHT + f"[browser-{self.ID}] " + Style.RESET_ALL + "Browser closed")
        

def url(value: str) -> str:
    if "http://" not in value and "https://" not in value:
        print(f"Specified url: {value} is not valid (add http/s://)")
        exit(1)
    return value


if __name__ == "__main__":
    parser = ArgumentParser(description="Ratuj zwierzaki mordo")
    parser.add_argument("laps", type=int, help="Liczba powtórzeń kliknięcia (na każdej z przeglądarek)")
    parser.add_argument("--timeout", type=int, help="Czas do odczekania po każdym like (domyślnie 1 sek)")
    parser.add_argument("--threads", type=int, help="Liczba wątków (przeglądarek) na raz (uwaga na zużycie RAMu!)")
    parser.add_argument("--max-timeout", type=int, help="Czas po jakim przeglądarka uznawana jest za martwą")
    parser.add_argument("--in-timeout", type=float, help="Czas do czekania wewnątrz klikania (1.5 def)")
    parser.add_argument("--url", type=url, help="Link do strony projektu")
    parser.add_argument("--not-headless", action="store_true", help="Nie chowa przeglądrek z widoku")
    parser.add_argument("--quiet", "-q", action="store_true", help="Program nie będzie nic wypisywał w konsoli")
    args = vars(parser.parse_args())

    LAPS: int = int(args['laps'])
    QUIET: bool = args['quiet']
    HEADLESS: bool = not args['not_headless']
    THREADS: int = int(args['threads']) if args['threads'] is not None else 1
    TIMEOUT: int  = int(args['timeout']) if args['timeout'] is not None else 1
    MAX_TIMEOUT: int = int(args['max_timeout']) if args['max_timeout'] is not None else 15
    IN_TIMEOUT: float = float(args['in_timeout']) if args['in_timeout'] is not None else 1.5

    if THREADS <= 0:
        print(Fore.RED + Style.BRIGHT + "[ERROR] [threads] Proszę o dodatnią wartość" + Style.RESET_ALL)
        exit(1)

    ratownicy = []
    for i in range(THREADS):
        print(f"[{i+1}/{THREADS}] Started")
        ratownicy.append(Ratownik(i, TIMEOUT, MAX_TIMEOUT, IN_TIMEOUT))

    START = datetime.now()
    last_printed = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
        for lap_id in range(LAPS):
            for ratownik in ratownicy:
                executor.submit(ratownik.save_animal)
                sleep(1)

            print(Fore.YELLOW + Style.BRIGHT + "[INFO]" + Fore.GREEN +  f" Saved {SAVED} animals in {(datetime.now() - START)}!" + Style.RESET_ALL)
            TO_GO = (LAPS-lap_id) * THREADS
            CPM = round(SAVED/(datetime.now() - START).total_seconds(),10)*60
            if CPM != 0:
                print(Fore.YELLOW + Style.BRIGHT + "[INFO]" + Fore.GREEN +  f" CPM: {CPM}, To go: {TO_GO/CPM} min." + Style.RESET_ALL)


    STOP = datetime.now()

    for ratownik in ratownicy:
        ratownik.close()

    print(Style.BRIGHT + f"========== Summary ==========" + Style.RESET_ALL)
    print(Style.BRIGHT + f"{'Browsers:':20} " + Style.RESET_ALL + f"{THREADS}")
    print(Style.BRIGHT + f"{'Timeout:':20} " + Style.RESET_ALL + f"{TIMEOUT} seconds")
    print(Style.BRIGHT + f"{'Saved animals:':20} " + Style.RESET_ALL + f"{SAVED}")
    print(Style.BRIGHT + f"{'Time:':20} " + Style.RESET_ALL + f"{str(STOP - START).split('.')[0]}")
    print(Style.BRIGHT + f"{'CPM:':20} " + Style.RESET_ALL + f"{round(SAVED/(datetime.now() - START).total_seconds(),10)*60}")

