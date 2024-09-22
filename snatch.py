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
from selenium.common.exceptions import TimeoutException

console = Console()


def get_driver():
    subprocess_Popen = subprocess.Popen
    subprocess.Popen = functools.partial(subprocess_Popen, process_group=0)
    driver = webdriver.Firefox()
    return driver


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


def check_captcha(driver, waitLoad: int = 0) -> bool:
    time.sleep(waitLoad)
    try:
        wait = WebDriverWait(driver, 60)
        if is_captcha_present(driver):
            console.print("[-]	Please solve the CAPTCHA in the browser window.", style="yellow")
            wait.until_not(EC.presence_of_element_located(By.XPATH, '//div[contains(@class, "captcha")]'))
            console.print("[+]	CAPTCHA solved! Proceeding...", style="green")
        return True
    except TimeoutException:
        console.print(f"[x]	Timeout while waiting for CAPTCHA completion. (You get 60 seconds)", style="red")
        driver.quit()
        os._exit(1)
    

def get_privacy_status(username) -> bool:
    console.print(f"[+]	Checking privacy status of {username}...", style="green")
    driver = get_driver()
    username = username.lstrip('@')
    driver.get(f'https://www.tiktok.com/@{username}')
    wait = WebDriverWait(driver, 60)
    wait.until_not(EC.title_is("Tiktok - Make Your Day"))
    time.sleep(1)
    if driver.title.split(".")[0] == "This account is private":
        console.print(f"\n[-]	Target account is private, you must login to an account that follows this user or exit.", style="yellow")
        return driver, True # Private account
    else:
        console.print(f"\n[+]	Target account is public, proceeding...", style="green")
        return driver, False # Public account


def get_user_videos(username, driver = None, isPrivate: bool = False) -> list[str | None]:
    if not driver:
        driver = get_driver()
    username = username.lstrip('@')
    url = f'https://www.tiktok.com/@{username}'
    if driver.current_url != url:
        driver.get(url)

    check_captcha(driver, 5)
    
    if isPrivate:
        console.print("[-]	Press Enter to continue after logging in... ", style="yellow")
        input()

    # Scroll to load all videos
    SCROLL_PAUSE_TIME = 2
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)

        check_captcha(driver)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    video_elements = driver.find_elements(By.XPATH, '//a[contains(@href, "/video/")]')
    video_urls = [elem.get_attribute('href') for elem in video_elements]
    video_urls = list(set(video_urls))
    return driver, video_urls


def extract_video_url(driver, url) -> str | None:
    driver.get(url)
    time.sleep(1)
    video_element = driver.find_element(By.TAG_NAME, 'video')
    video_url = driver.execute_script("return arguments[0].currentSrc;", video_element)

    if video_url:
        return video_url
    else:
        console.print("[x]	No video URL found in the video element.", style="red")
        return None


def download_video(driver, source_url, download_dir: str = None):
    
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
        console.print("[+]	Opening in browser...", style="green")
        driver.get(source_url)
        console.print("[-]	Please use your browser's functionality to download the video.", style="yellow")
        input("After downloading the video, press Enter to continue...")


def download_all(urls, driver = None, download_dir: str = None, auto_download: bool = False) -> None:
    if not driver:
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


if __name__ == "__main__":
    username = "@username"
    video_urls = get_user_videos(username)
    download_all(video_urls)