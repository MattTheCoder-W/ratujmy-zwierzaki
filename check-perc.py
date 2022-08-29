from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from time import sleep


def check_perc():
    opt = Options()
    opt.headless = True
    driver = webdriver.Firefox(options=opt)
    driver.get("https://whatwevalue.telekom.com/pl-PL/projects/2B7EbLBBdvXrBQsGbhIasl")
    sleep(2)
    place = driver.find_elements(By.XPATH, '/html/body/div/div/div[1]/main/div/div[9]/div[2]/div[1]/div[1]/p[2]')[0]
    txt = driver.find_elements(By.XPATH, '/html/body/div/div/div[1]/main/div/div[9]/div[2]/div[1]/div[2]/p')[0]
    print("Miejsce", place.get_attribute("innerText"), txt.get_attribute("innerText"))


if __name__ == "__main__":
    check_perc()
