import dropbox
import os
import requests
import time
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from db_server import InstaDbService


class InstaParser:
    def __init__(self, username, password):
        self.username = username
        # self.username = 'ihor_yanovchyk'
        self.password = password
        self.browser = None

        self.db = InstaDbService()

    def start_browser(self, mobile=False):
        """Start new browser session

        :param mobile: True if need run mobile version.
        """

        option = webdriver.ChromeOptions()

        if mobile:
            mobile_emulation = {"deviceName": "Nexus 5"}
            option.add_experimental_option("mobileEmulation", mobile_emulation)
            self.browser = webdriver.Chrome('./drivers/chromedriver', desired_capabilities=option.to_capabilities())
        else:
            # option.add_argument("user-data-dir=/home/yura/.config/google-chrome/Default")
            self.browser = webdriver.Chrome('./drivers/chromedriver', chrome_options=option)
            # self.browser = webdriver.Remote("http://localhost:4444/wd/hub", webdriver.DesiredCapabilities.CHROME.copy())
            # self.browser.maximize_window()

        self.browser.implicitly_wait(10)

    def login(self, mobile=False):
        """Login to Instagram"""
        if not self.browser:
            self.start_browser(mobile=mobile)
        self.browser.get("https://www.instagram.com/accounts/login/")

        username = self.browser.find_element_by_name('username')
        username.clear()
        username.send_keys(self.username)
        password = self.browser.find_element_by_name('password')
        password.clear()
        password.send_keys(self.password)
        password.submit()

        # Close modal windows
        self.browser.implicitly_wait(1)
        try:
            self.browser.find_element_by_xpath("//button[contains(.,'Not Now')]").click()
        except:
            pass

        try:
            self.browser.find_element_by_xpath("//button[contains(.,'Cancel')]").click()
        except:
            pass
        self.browser.implicitly_wait(10)

    def parse_permalink(self):
        """Parse permalink for post from saved tab and save to db"""
        self.browser.get("https://www.instagram.com/{}/saved/".format(self.username))
        while self.browser.find_elements_by_xpath("//a[contains(@href,'/p/')]"):
            # self.browser.execute_script("window.scrollTo(0, 100);")
            els = self.browser.find_elements_by_xpath("//a[contains(@href,'/p/')]")
            for i in els:
                try:
                    insta_url = i.get_attribute("href")
                    # print(insta_url)

                    self.db.add_new_saved_post(insta_url)

                    # Remove element from page

                    # self.browser.execute_script("""
                    # var a = arguments[0];
                    # a.parentNode.removeChild(a);
                    # """, i)
                except:
                    print('\nSOME ERROR!!!!\n')
                    pass

            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

    def parse_additional_info(self):
        """
        Parse additional information for post that is not parsed yet,
        Upload photo to dropbox and update info in db.
        """

        rows = self.db.get_urls_for_parse_info()
        for i in rows:
            self.browser.get(i[1])
            try:
                content = self.browser.find_element_by_xpath("//div/video").get_attribute("src")
            except:
                content = self.browser.find_element_by_xpath("//div/img[contains(@src, 'https://instagram')]").get_attribute("src")
            owner_url = self.browser.find_element_by_xpath("//header//a").get_attribute("href")
            owner_name = self.browser.find_element_by_xpath("//header//a[contains(@class, 'notranslate')]").get_attribute("title")

            # Get photo and upload to dropbox
            r = requests.get(content, allow_redirects=True)
            access_token = 'rO7DzTSod8AAAAAAAAAAazeDmyn6AfsaEpdPIOO-HAEPcBXjkiZdcvXDTgAgAvLh'
            dbx = dropbox.Dropbox(access_token)

            upload_results = dbx.files_upload(r.content, '/photo_files/{}.{}'.format(i[0], r.headers['content-type'].split('/')[-1]))

            self.db.update_post_row((upload_results.id, owner_url, owner_name, i[0]))

    def post_new_image(self):
        """Post new image"""
        # new_post_btn = self.browser.find_element_by_xpath("//span[@aria-label='New Post']")
        # new_post_btn.click()

        # actions = ActionChains(self.browser)
        # element = self.browser.find_element_by_xpath("//span[@aria-label='New Post']")
        # actions.move_to_element(element)
        # actions.click()
        # actions.send_keys(os.getcwd() + "/python.png")
        # actions.perform()
        #
        # test = self.browser.find_elements_by_xpath("//input[@accept='image/jpeg']")[2]
        # test.send_keys(os.getcwd() + "/python.png")
        # test.submit()
        from InstagramAPI import InstagramAPI
        api = InstagramAPI("therealbooty_squad", "nmvETGay")
        api.login()
        api.uploadPhoto(os.getcwd() + "/python.jpg")
        pass

    def close_browser(self):
        """Close browser if it opened"""
        if self.browser:
            try:
                self.browser.close()
            except:
                pass
            self.browser = None


parse = InstaParser('therealbooty_squad', 'nmvETGay')
# parse.login(mobile=True)
parse.post_new_image()
# parse.parse_permalink()
# parse.parse_additional_info()
parse.close_browser()