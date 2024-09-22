import time, os, sys
from colorama import Fore
from snatch import download_all, get_user_videos


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


def download_everything(target_username: str, auto_download: bool = False):

    download_dir: str = os.path.join(os.getcwd(), target_username)
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    urls: list[str | None] = get_user_videos(target_username)
    if urls:
        print(Fore.GREEN, '\n[+]	Successfully snatched all video urls\n')
    download_all(urls, download_dir, auto_download)
    
    time.sleep(1)
    print(Fore.GREEN, '\n[+]	Snatch Successfull !\n')


def main():
    
    print("[+]	Enter 'list' to read from file accounts.txt")
    target_username = input("[+]	Enter Target Username -->  ")
    if target_username == "list":
        if os.path.exists('accounts.txt') == False:
            print(Fore.RED, "[+]	accounts.txt not found")
            sys.exit()
        with open('accounts.txt', 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line:
                    download_everything(line.strip(), True) # REMOVE True TO DISABLE AUTO DOWNLOAD
                    time.sleep(1)
                    show_title(instant=True)
                
    else:
        download_everything(target_username, True) # REMOVE True TO DISABLE AUTO DOWNLOAD

     
if __name__ == "__main__":     
    show_title()     
    main()