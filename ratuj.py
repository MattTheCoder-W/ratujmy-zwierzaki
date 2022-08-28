from time import sleep
from argparse import ArgumentParser
import concurrent.futures
import geckodriver_autoinstaller

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options


class Ratownik:
    def __init__(self, obj_id: int) -> None:
        self.ID = obj_id
        self.laps = 0
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)
        self.wait = WebDriverWait(self.driver, 5)
        self.page_url = "https://whatwevalue.telekom.com/pl-PL/projects/2B7EbLBBdvXrBQsGbhIasl"
        self.cookies_accept_xpath = "/html/body/div/div/div[1]/main/div[1]/div[2]/div/div[2]/div[2]/button[1]"
        self.like_xpath = "/html/body/div/div/div[1]/main/div/div[9]/div[2]/div[2]/button"
        self.TIMEOUT = 1

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
        prefix = f"[browser-{self.ID}, lap={self.laps}]"
        print(f"{prefix} Saving animal in progress")
        self.driver.get(self.page_url)
        sleep(1)
        self.wait.until(self.get_accept_cookies)
        self.get_accept_cookies(None)[0].click()
        self.driver.execute_script('document.querySelector(".boost-us-button").scrollIntoView();')
        sleep(0.5)
        self.driver.find_elements(By.XPATH, self.like_xpath)[0].click()
        self.laps += 1

        print(f"{prefix} Animal saved!")
        self.clear_cookies()
        print(f"{prefix} INFO: Cookies cleared, waiting {self.TIMEOUT} seconds before restart")
        sleep(self.TIMEOUT)

    def close(self) -> None:
        self.driver.quit()
        print(f"[browser-{self.ID}] Browser closed")
        

if __name__ == "__main__":
    parser = ArgumentParser(description="Ratuj zwierzaki mordo")
    parser.add_argument("laps", type=int, help="Liczba powtórzeń kliknięcia (na każdej z przeglądarek)")
    parser.add_argument("--threads", "-t", type=int, help="Liczba wątków (przeglądarek) na raz (uwaga na zużycie RAMu!)")
    parser.add_argument("--not-headless", action="store_true", help="Nie chowa przeglądrek z widoku")
    parser.add_argument("--quiet", "-q", action="store_true", help="Program nie będzie nic wypisywał w konsoli")
    args = vars(parser.parse_args())

    print("Checking for geckodriver...")
    geckodriver_autoinstaller.install()

    LAPS: int = int(args['laps'])
    QUIET: bool = args['quiet']
    HEADLESS: bool = not args['not_headless']
    THREADS: int = int(args['threads']) if args['threads'] is not None else 1

    if THREADS <= 0:
        print("Proszę o dodatnią wartość")
        exit(1)

    ratownicy = []
    for i in range(THREADS):
        ratownicy.append(Ratownik(i))

    with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
        for lap_id in range(LAPS):
            for ratownik in ratownicy:
                executor.submit(ratownik.save_animal)

    for ratownik in ratownicy:
        ratownik.close()

