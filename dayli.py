#daily post

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import time
import os
import autoit
import pyperclip
import schedule
from datetime import date
from datetime import datetime

def job():
    print("enter job()")
    path = "C:\\Users\\You\\Desktop\\temp\\data\\"
    dirs = os.listdir( path )

    for file in dirs:
        if file.startswith(str(date.today())) and file.endswith('jpg'):
            print('DATE OK')
            global jpg_to_post
            jpg_to_post = path + file
            post()
        elif file.startswith(str(date.today())) and file.endswith('html'):
            global path_to_html_to_copy
            path_to_html_to_copy = path + file

def post():
    print("enter post()")
    print(jpg_to_post)
    print(path_to_html_to_copy)
    mobile_emulation = { "deviceName": "Nexus 5" }
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    driver=webdriver.Chrome("./chromedriver", desired_capabilities = chrome_options.to_capabilities())
    driver.get('https://www.instagram.com/accounts/login/')
    time.sleep(2)
    user_name=driver.find_element_by_xpath("//input[@name='username']")
    user_name.send_keys('your_username')
    password=driver.find_element_by_xpath("//input[@name='password']")
    password.send_keys('your_password')
    driver.find_element_by_xpath("//form/span/button[text()='Log in']").click()
    # time.sleep(2)
    # driver.find_element_by_xpath("//a[text()='Not Now']").click()
    time.sleep(2)
    driver.find_element_by_xpath("//*[@class='_k0d2z _ttgfw _mdf8w']").click()
    time.sleep(2)
    autoit.win_active("Open")
    autoit.control_set_text("Open","Edit1",jpg_to_post)
    autoit.control_send("Open","Edit1","{ENTER}")
    time.sleep(2)
    try:
        driver.find_element_by_xpath("//button[@class='_j7nl9']").click()
    except Exception:
        pass
    driver.find_element_by_xpath("//button[text()='Next']").click()
    time.sleep(2)
    fo = open(path_to_html_to_copy, 'r', encoding="utf8").read()
    pyperclip.copy(fo)
    time.sleep(2)
    driver.find_element_by_xpath("//*[@class='_qlp0q']").send_keys(Keys.CONTROL, 'v')
    time.sleep(2)
    driver.find_element_by_xpath("//button[text()='Share']").click()
    time.sleep(10)
    driver.quit()

schedule.every().day.at("21:30").do(job)

while True:
    schedule.run_pending()
    time.sleep(20)