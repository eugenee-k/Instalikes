from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import time, requests, base64
from db_utils import *


def driver_init():
    """
    initialize and return a webdriver instance
    """
    options = webdriver.ChromeOptions()

    options.add_argument("--start-maximized")
    options.add_argument("--incognito")
    options.add_argument("--headless")

    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)

    return driver

#tdhrnmdkrlvhdtpgh
def scrape_likes(driver, userid):
    driver.get('https://www.instagram.com/your_activity/interactions/likes')
    jsn = []

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 
                'div > div > div.wbloks_1.wbloks_74 > div > div > div > div > '
                'div:nth-child(3) > div > div > div > div > div > div')))
    except TimeoutException:
        return jsn

    # Scroll down to load more likes
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:  
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(2)   
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            break
        last_height = new_height

    total = len(driver.find_elements(By.CSS_SELECTOR, 
                'div > div > div.wbloks_1.wbloks_74 > div > div > div > div > '
                'div:nth-child(3) > div > div > div > div > div > div'))

    for i in range(1, total+1):
        driver.find_element(By.CSS_SELECTOR, 
            'div > div > div.wbloks_1.wbloks_74 > div > div > div > div > '
            'div:nth-child(3) > div > div > div > div > div > div:nth-child({})'.format(i)
        ).click()

        images = []

        while True:
            try:
                WebDriverWait(driver, 9).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 
                        'div > div > div > ul > li > div > div > div > div > div._aagv > img')))
                imgs = driver.find_elements(By.CSS_SELECTOR, 
                        'div > div > div > ul > li > div > div > div > div > div._aagv > img')

                for img in imgs:
                    src = img.get_attribute('src')
                    image = bytearray(requests.get(src).content)

                    if image not in images:
                        images.append(image)

                driver.find_element(By.CSS_SELECTOR, 'button[aria-label=Next]').click()
                time.sleep(0.5)
            except (NoSuchElementException, TimeoutException): 
                break

        if len(images) == 0:
            break

        if len(images) < 10:
            images += [''] * (10 - len(images))

        try:
            user = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div > span > div > div'))).text.split('\n')[0]
        except TimeoutException:
            user = ''

        try:
            caption = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div > span > div > span'))).text
        except TimeoutException:
            caption = ''

        try:
            comments = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 
                    'section > main > div > div.x6s0dn4 > div > div.x4h1yfo > div > div.x5yr21d')))
            last_height = driver.execute_script('return arguments[0].scrollHeight', comments)

            while True:
                driver.execute_script('arguments[0].scrollTo(0, arguments[0].scrollHeight)', comments)
                time.sleep(2)   
                new_height = driver.execute_script('return arguments[0].scrollHeight', comments)
                
                if new_height == last_height:
                    break

                last_height = new_height
                comments = driver.find_element(By.CSS_SELECTOR, 
                    'section > main > div > div.x6s0dn4 > div > div.x4h1yfo > div > div.x5yr21d')

            replies = driver.find_elements(By.XPATH, "// span[contains(text(), 'View all ')]")
            for reply in replies:
                driver.execute_script('arguments[0].click()', reply)
                time.sleep(0.2)
            time.sleep(1)

            comments = driver.find_element(By.CSS_SELECTOR, 
                'section > main > div > div.x6s0dn4 > div > div.x4h1yfo > div > div.x5yr21d').text
        except TimeoutException:
            comments = ''

        print(user)
        print(caption)
        #print(comments)

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM instalikes.likes WHERE userid = %s AND image1 = %s AND image2 = %s AND image3 = %s", 
            (userid, images[0], images[1], images[2]))
        existing_entry = cursor.fetchone()
        cursor.close()

        if existing_entry:
            break

        im_data = []
        for image in images:
            if image:
                im_data.append(base64.b64encode(image).decode('utf-8'))
            else:
                im_data.append('')

        add_like(userid, images, user, caption, comments)
        jsn.append({'user': user, 'caption': caption, 'comments': str(comments), 'image': im_data})

        driver.get('https://www.instagram.com/your_activity/interactions/likes')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 
                'div > div > div.wbloks_1.wbloks_74 > div > div > div > div > '
                'div:nth-child(3) > div > div > div > div > div > div')))

    return jsn


def scrape_comments(driver, userid):
    driver.get('https://www.instagram.com/your_activity/interactions/comments')
    jsn = []

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 
                'div > div > div > div > div:nth-child(3) > div > div > div > div:nth-child(1)')))
    except TimeoutException:
        return jsn

    # Scroll down to load more comments
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:  
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(2)   
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            break
        last_height = new_height

    total = len(driver.find_elements(By.CSS_SELECTOR, 
                'div > div > div > div > div:nth-child(3) > div > div > div > div'))

    for i in range(1, total):
        try:
            comment = driver.find_element(By.CSS_SELECTOR, 
                'div > div > div > div > div:nth-child(3) > div > div > div > div:nth-child({})'.format(i)
            ).text
            img = driver.find_element(By.CSS_SELECTOR, 
                'div > div > div > div > div:nth-child(3) > div > div > div > div:nth-child({}) > '
                'div:nth-child(1) > div > div > div > div > div > div:nth-child(2) > div > img'.format(i))
            src = img.get_attribute('src')
            image = bytearray(requests.get(src).content)

            print(comment)

            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM instalikes.comments WHERE userid = %s AND image = %s", (userid, image))
            existing_entry = cursor.fetchone()
            cursor.close()

            if existing_entry:
                break

            add_comment(userid, image, comment)
            jsn.append({'comment': comment, 'image': base64.b64encode(image).decode('utf-8')})
        except NoSuchElementException:
            break

    return jsn
