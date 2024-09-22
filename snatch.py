import functools
import subprocess
import time
import os
import requests

from rich.console import Console
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

console = Console()
ERRORLEVEL = 0

def get_driver(downloading: bool = False, download_dir: str = None):
    # Returns a web driver and makes it play nicely with interrupt signals
    subprocess_Popen = subprocess.Popen
    subprocess.Popen = functools.partial(subprocess_Popen, process_group=0)
    if downloading:
        profile = webdriver.FirefoxProfile()
        profile.set_preference('browser.download.folderList', 2) 
        profile.set_preference('browser.download.dir', download_dir)
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'video/mp4,video/mpeg,video/quicktime,video/x-ms-wmv,video/x-flv,video/webm')
        profile.set_preference('browser.download.manager.showWhenStarting', False)
        profile.set_preference('browser.download.manager.useWindow', False)
        profile.set_preference('browser.download.manager.focusWhenStarting', False)
        profile.set_preference('browser.download.manager.alertOnEXEOpen', False)
        profile.set_preference('browser.download.manager.showAlertOnComplete', False)
        profile.set_preference('browser.download.manager.closeWhenDone', True)
        
        options = Options()
        options.profile = profile
        driver = webdriver.Firefox(options=options.profile)
    else:
        driver = webdriver.Firefox()
    subprocess.Popen = subprocess_Popen
    return driver


def extract_video_url(driver, url) -> str | None:
    driver.get(url)
    try:      
        wait = WebDriverWait(driver, 60)
        if is_captcha_present(driver):
            console.print("[-]	Please solve the CAPTCHA in the browser window.", style="yellow")
            wait.until_not(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "captcha")]')))
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'video')))
    except Exception as e:
        console.print(f"[x]	Error or timeout while waiting for video element: {e}", style="red")
        return None
    video_element = driver.find_element(By.TAG_NAME, 'video')
    video_url = driver.execute_script("return arguments[0].currentSrc;", video_element)

    if video_url:
        return video_url
    else:
        console.print("[x]	No video URL found in the video element.", style="red")
        return None

def is_captcha_present(driver) -> bool:
    captcha_elements = [
        (By.XPATH, '//div[contains(@class, "captcha")]'),
        (By.XPATH, '//iframe[contains(@src, "captcha")]'),
    ]
    for by, value in captcha_elements:
        try:
            driver.find_element(by, value)
            return True
        except:
            continue
    return False


def get_user_videos(username) -> list[str | None]:
    # Create the link from the username
    username = username.lstrip('@')
    url = f'https://www.tiktok.com/@{username}'

    driver = get_driver()
    driver.get(url)

    wait = WebDriverWait(driver, 600)  # Keep the webdriver active for up to 10 minutes

    time.sleep(5) # Wait 5 seconds for the page to load
    # Check for CAPTCHA
    if is_captcha_present(driver):
        console.print("[-]	Please solve the CAPTCHA in the browser window.", style="yellow")
        wait.until_not(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "captcha")]')))

    # Scroll to load all videos
    SCROLL_PAUSE_TIME = 2
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)

        if is_captcha_present(driver):
            console.print("[-]	Please solve the CAPTCHA in the browser window.", style="yellow")
            wait.until_not(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "captcha")]')))
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            console.print(f"[+]	Successfully loaded all videos", style="green")
            break
        last_height = new_height

    video_elements = driver.find_elements(By.XPATH, '//a[contains(@href, "/video/")]')
    video_urls = [elem.get_attribute('href') for elem in video_elements]
    video_urls = list(set(video_urls))
    driver.quit()
    return video_urls


def download_all(urls, download_dir: str = None, auto_download: bool =False) -> None:
    driver = get_driver()
    global filename
    filename = 0
    for url in urls:
        source_url = extract_video_url(driver, url)
        if source_url:
            filename += 1
            console.print(f"[+]	Extracted source URL: {source_url}", style="green")
            download_video(driver, source_url, download_dir if auto_download else None)
        else:
            console.print("[x]	Failed to extract video URL.", style="red")
    driver.quit()

def download_video(driver, source_url, download_dir: str = None):
    console.print("[+]	Opening in browser...", style="green")
    driver.get(source_url)
    
    if download_dir:
        # Automatic download procedure
        console.print("[+]	Extracting cookies from browser session...", style="green")
        selenium_cookies = driver.get_cookies()
        session = requests.Session()
        for cookie in selenium_cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        headers = {
            'User-Agent': driver.execute_script("return navigator.userAgent;"),
            'Referer': source_url,
        }
                
        try:
            global filename
            file_path = os.path.join(download_dir, f"{filename:04}.mp4")
            console.print(f"[+]	Downloading video {filename:04} to {download_dir}", style="green")

            response = session.get(source_url, headers=headers, stream=True)
            response.raise_for_status()

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            console.print(f"[+]	Video downloaded successfully to {file_path}", style="green")
            return file_path

        except Exception as e:
            console.print(f"Error downloading video: {e}", style="red")
            return None
    else:
        # Manual download procedure
        console.print("[-]	Please use your browser's functionality to download the video.", style="yellow")
        input("After downloading the video, press Enter to continue...")



if __name__ == "__main__":
    username = "@username"
    video_urls = get_user_videos(username)
    download_all(video_urls)