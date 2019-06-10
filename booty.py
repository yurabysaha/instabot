import json

import dropbox
import os

import imageio
import requests
import time
import random
import schedule
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from InstagramAPI import InstagramAPI, VideoFileClip
from db_server import InstaDbService

CONFIG = {}

# Load Config Data
with open('./config.json') as config_f:
    default_config = json.load(config_f)
    for key, value in default_config.items():
        CONFIG[key] = os.getenv(key, value)


class InstaParser:
    def __init__(self, username, password):
        self.username = username
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
            option.add_argument("user-data-dir=/home/yura/.config/google-chrome/Default")
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
        self.browser.implicitly_wait(1)
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
            dbx = dropbox.Dropbox(CONFIG['DROPBOX_ACCESS_TOKEN'])

            upload_results = dbx.files_upload(r.content, '/photo_files/{}.{}'.format(i[0], r.headers['content-type'].split('/')[-1]))

            self.db.update_post_row((upload_results.id, owner_url, owner_name, i[0]))

    def post_new_image(self):
        """Post new image"""

        dbx = dropbox.Dropbox(CONFIG['DROPBOX_ACCESS_TOKEN'])

        unposted_posts = self.db.get_unposted_posts().fetchall()

        if unposted_posts:
            next_post = random.choice(unposted_posts)

            file_info = dbx.files_get_metadata(next_post[2])
            file_extension = file_info.name.split('.')[-1]
            saved_file_path = os.getcwd() +'/downloads/tmp.' + file_extension
            dbx.files_download_to_file(saved_file_path, next_post[2])

            api = InstagramAPI(self.username, self.password)
            api.login()

            text_for_post = self.prepeare_text_for_post(next_post)

            if file_extension == 'jpeg':
                api.uploadPhoto(saved_file_path, caption=text_for_post)
            else:
                clip = VideoFileClip(saved_file_path)
                clip.save_frame(os.getcwd() + "/downloads/thumbnail.jpeg", t=2)  # saves the frame a t=2s

                api.uploadVideo(saved_file_path, os.getcwd() + '/downloads/thumbnail.jpeg', caption=text_for_post)

            self.db.mark_as_posted(next_post[0])

        else:
            print('No post for posting!!!')

    def close_browser(self):
        """Close browser if it opened"""
        if self.browser:
            try:
                self.browser.close()
            except:
                pass
            self.browser = None

    def prepeare_text_for_post(self, post):

        available_hashtags = [
            "#booty🍑", "#fitgirl", "#fitfam", "#modelsofinstagram",
            "#instabooty", "#instabootylicious", "#bigbutt", "#pantyhose", "#fishnets", "#tights",
            "#whitegirlsevolving", "#bigbootywhitegirl", "#bootylover", "#bootybooty",
            "#teamnaturalbooty", "#bigbuttsdontlie#whootybooty", "#whootywednesday",
            "#slimthickgirls", "#slimthick #bubblebutt", "#curves", "#sexycurves", "#bootyislife",
            "#thatass", "#phatbutt", "#instabootylicious", "#asssofine", "#instabooty", "#pantyhose",
            "#pantyhosegirl", "#blacktights", "#tights", "#bootyfull", "#assassasss", "#bubblebooty",
            "#bootylover", "#bootybooty", "#assfordays", "#assassass", "#bootysofine",
            "#bigbuttsdontlie", "#whootybooty", "#whootywednesday", "#whitegirlsevolving",
            "#bigbootywhitegirls", "#picoftheday", "#miamimodel", "#vegasmodel", "#lamodel", "#bootytransformation",
            "#fitnessmotivation", "#fitgoals", "#fitspo", "#bodyempowerment", "#healthylifestyle",
            "#freethenipplemovement", "#fitnessmotivation", "#wshhfitness",
            "#miamimodel", "#fitnessmodel", "#instafitness", "#fitnessaddict", "#humpday",
            "#thebooty", "#belfie", "#bootygainz", "#ycmediainc", "#girlswholift", "#datbooty",
            "#model", "#miamimodel", "#lasvegasmodel"
        ]
        available_messages = [
            "Do you like it?", "Tag your friend who wants to eat this peachy", "What do you think, Comment it!",
            "Like it?", "Give your feedback in  Comment", "Love it?", "Tag your partner in crime!",
            "This beauty is one of the our favourite up and coming models", "Give her a follow, she has a bright future",
            "What`s in your fridge?", "therealbooty_squad", "Who wants this baby?",
            "What`s your favourite thing about 🍑?", "Need your opinion!", "Few comments for this baby!",
            "Woow, nice shot!", "Look at this girl!", "Look at this!", "Just a cool shot in your feed!",
            "Looks good, yeah?"
        ]

        result = '🍑 {} 🍑\n\nModel: @{}\nPhoto: @therealbooty_squad\n\n#therealbooty_squad '.format(
            random.choice(available_messages),
            post[4]
        )

        result += ' '.join(str(e) for e in random.sample(available_hashtags, random.randrange(15,25)))
        return result


parse = InstaParser(CONFIG['INSTA_USERNAME'], CONFIG['INSTA_PASSWORD'])

# Parse functionality.

# parse.login(mobile=False)
# parse.post_new_image()
# parse.parse_permalink()
# parse.parse_additional_info()
# parse.close_browser()

# Set schedule for posting new post.
schedule.every(4).hours.do(parse.post_new_image)
# schedule.every(6).minutes.do(parse.post_new_image)

while True:
    # Checks whether a scheduled task is pending to run or not
    schedule.run_pending()
    time.sleep(1)
