import time, os
from colorama import Fore
from snatch import download_all, get_user_videos, get_privacy_status

# HARDCODED VARIABLES, CHANGE HOW PROGRAM WORKS
doAutoDownload: bool = True     # Change to False to manually complete all downloads

def typewriter_animation(message):
    for char in message:
        print(char, end='', flush=True)
        time.sleep(0.005)
    print()


def show_title(instant: bool = False):
    os.system("title TikSnatch")
    os.system("cls")
    print(Fore.GREEN , "")
    
    title = '''
    
████████╗██╗██╗  ██╗███████╗███╗   ██╗ █████╗ ████████╗ ██████╗██╗  ██╗
╚══██╔══╝██║██║ ██╔╝██╔════╝████╗  ██║██╔══██╗╚══██╔══╝██╔════╝██║  ██║
   ██║   ██║█████╔╝ ███████╗██╔██╗ ██║███████║   ██║   ██║     ███████║
   ██║   ██║██╔═██╗ ╚════██║██║╚██╗██║██╔══██║   ██║   ██║     ██╔══██║
   ██║   ██║██║  ██╗███████║██║ ╚████║██║  ██║   ██║   ╚██████╗██║  ██║
   ╚═╝   ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝

    '''
    if instant:
        print(title, end='', flush=True)
    else:
        typewriter_animation(title)


def download_everything(targetUsername: str, doAutoDownload: bool = False):
    driver, isPrivate = get_privacy_status(targetUsername)
    
    driver, urls = get_user_videos(targetUsername, driver, isPrivate) 
    if urls:
        print(Fore.GREEN, '\n[+]	Successfully snatched all video urls\n')
    else:
        print(Fore.RED, '\n[x]	An error occurred in snatching video urls\n')
        driver.quit()
        os._exit(1)
    
    download_dir: str = os.path.join(os.getcwd(), targetUsername)
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    download_all(urls, driver, download_dir, doAutoDownload)
    
    print(Fore.GREEN, '\n[+]	Snatch Successful !\n')


def main():
    global doAutoDownload
    
    print("[+]	Enter 'list' to read from file accounts.txt")
    targetUsername = input("[+]	Enter Target Username -->  ")
    if targetUsername == "list":
        if os.path.exists('accounts.txt') == False:
            print(Fore.RED, "[+]	accounts.txt not found")
            os._exit(1)
        with open('accounts.txt', 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line:
                    download_everything(line.strip(), doAutoDownload)
                    time.sleep(1)
                    show_title(instant=True)
                
    else:
        download_everything(targetUsername, doAutoDownload)


if __name__ == "__main__":     
    show_title()     
    main()