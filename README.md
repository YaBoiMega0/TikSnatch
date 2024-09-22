# What is this?
Using _selenium_ and some manual user input, this script automatically downloads all videos of one or more TikTok users.
A rewrite of [TikTokLoader](https://github.com/NicoWeio/TikTokLoader) that... works.

# Setup and usage
- Create a python 3.12.1 venv in a folder called ".venv" with `py -m venv .\.venv` then enter the venv by running `.\.venv\Scripts\activate` in the terminal
- Run `pip install -r requirements.txt` (specific versions probably not needed but recommended)
- Double click `run.bat` if on windows and follow instructions
- On other OS's, run `main.py` directly and edit the username variable at the bottom of the script (account picker functionality is not supported outside windows)

# How does it work?
- The script first collects a username or list of several usernames from an accounts.txt file if you want several accounts to be downloaded without having to watch them all
- It then opens a selenium firefox browser and gets the user to manually complete a CAPTCHA test, this convinces TikTok to trust that browser session, so all the rest of the downloading is done by copying the cookies and headers of that browser session to all requests.
- It scrolls to the bottom of a users profile page to load every video, and uses the selenium webdriver built in `find_elements` to get the URL of all videos.
- It then accesses each video one by one, generating a one time access source URL (which is printed to the terminal) and then downloads the video from there using requests (and the verified browser session details)
- The videos are saved in incremental numbers in a subfolder copying the username inputted.

> [!WARNING]
> THE SCRIPT MAY ONLY BE USED IN ACCORDANCE WITH TIKTOK TERMS OF SERVICE, I AM NOT RESPONSIBLE FOR ANY MISUSE