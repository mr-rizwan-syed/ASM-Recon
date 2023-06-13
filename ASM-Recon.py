import sys
import os
import subprocess
from colorama import init, Fore, Style

banner = '''
     _    ____  __  __       ____                      
    / \  / ___||  \/  |     |  _ \ ___  ___ ___  _ __  
   / _ \ \___ \| |\/| |_____| |_) / _ \/ __/ _ \| '_ \ 
  / ___ \ ___) | |  | |_____|  _ <  __/ (_| (_) | | | |
 /_/   \_\____/|_|  |_|     |_| \_\___|\___\___/|_| |_|  @rushikeshhh-patil                                   
'''

print(Fore.YELLOW + Style.BRIGHT + banner + Style.RESET_ALL + Fore.RESET)

banner2 = '''

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  Usage : python3 ASM-Recon.py https://test.com project_name 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

'''
print(Fore.YELLOW + Style.BRIGHT + banner2 + Style.RESET_ALL + Fore.RESET)

separator = '''-----------------------------------------------------------------------------------------------------------------------------------'''

def nuclei(url, project_name):
    nuclei_command = f'nuclei -u {url} -o {os.path.join("results", project_name, "nuclei.txt")}'
    try:
        subprocess.run(nuclei_command, shell=True, check=True)
        print(Fore.GREEN + Style.BRIGHT + "\nNuclei scanning completed." + Style.RESET_ALL + Fore.RESET)
    except subprocess.CalledProcessError as e:
        print(Fore.RED + Style.BRIGHT + f"\nError running Nuclei Scan: {e}" + Style.RESET_ALL + Fore.RESET)
        return

def gobuster(url, project_name):
    dirsearch_command = f'gobuster dir -u {url} -w /usr/share/dirb/wordlists/dicc.txt -o {os.path.join("results", project_name, "gobuster.txt" )} 2>/dev/null'
    try:
        subprocess.run(dirsearch_command, shell=True, check=True)
        print(Fore.GREEN + Style.BRIGHT + "\nDirectory bruteforcing completed." + Style.RESET_ALL + Fore.RESET)
    except subprocess.CalledProcessError as e:
        print(Fore.RED + Style.BRIGHT + f"\nError running Directory Searching: {e}" + Style.RESET_ALL + Fore.RESET)
        return

def gather_js_files(url, project_name):
    katana_command = f'katana -u {url} | grep ".js$" | tee {os.path.join("results", project_name, "katana_output.txt")}'
    waybackurls_command = f'gau {url} | grep "\.js$" | tee {os.path.join("results", project_name, "gau_output.txt")}'
    try:
        subprocess.run(katana_command, shell=True, check=True)
        subprocess.run(waybackurls_command, shell=True, check=True)
        print(Fore.GREEN + Style.BRIGHT + "JS file gathering completed." + Style.RESET_ALL + Fore.RESET)
    except subprocess.CalledProcessError as e:
        print(Fore.RED + Style.BRIGHT + f"Error running Katana or Waybackurls: {e}" + Style.RESET_ALL + Fore.RESET)
        return

    with open(os.path.join("results", project_name, "katana_output.txt"), "r") as katana_file:
        katana_output = katana_file.read().strip().split("\n")

    with open(os.path.join("results", project_name, "gau_ouput.txt"), "r") as waybackurls_file:
        gau_ouput = waybackurls_file.read().strip().split("\n")

    js_files = set(katana_output + gau_ouput)

    with open(os.path.join("results", project_name, "js_files.txt"), "w") as output_file:
        output_file.write("\n".join(js_files))

    print(Fore.GREEN + Style.BRIGHT + "JS files saved in js_files.txt" + Style.RESET_ALL + Fore.RESET)

def get_live_urls_from_file(filename, project_name):
    httpx_command = f'httpx -l {filename} -silent'
    try:
        result = subprocess.run(httpx_command, shell=True, check=True, capture_output=True, text=True)
        output = result.stdout.strip()
        if output:
            live_urls = output.split("\n")
            with open(os.path.join("results", project_name, "live_js_urls.txt"), "w") as file:
                for url in live_urls:
                    file.write(url + "\n")
            print(Fore.GREEN + "Live URLs saved to live_js_urls.txt" + Fore.RESET)
        else:
            print(Fore.YELLOW + "No .js live URLs found." + Fore.RESET)
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"Error running httpx on {filename}: {e}" + Fore.RESET)

def httpx(js_files, project_name):
    get_live_urls_from_file(os.path.join("results", project_name, "js_files.txt"), project_name)

if len(sys.argv) < 3:
    sys.exit(1)

url = sys.argv[1]
project_name = sys.argv[2]

if not os.path.exists("results"):
    os.makedirs("results", exist_ok=True)

project_dir = os.path.join("results", project_name)
if not os.path.exists(project_dir):
    os.makedirs(project_dir, exist_ok=True)

init()

# Function Calls
nuclei(url, project_name)
print(Fore.YELLOW + Style.BRIGHT + separator + Style.RESET_ALL + Fore.RESET)
gobuster(url, project_name)
print(Fore.YELLOW + Style.BRIGHT + separator + Style.RESET_ALL + Fore.RESET)
gather_js_files(url, project_name)
print(Fore.YELLOW + Style.BRIGHT + separator + Style.RESET_ALL + Fore.RESET)

js_files = []
with open(os.path.join("results", project_name, "js_files.txt"), "r") as js_file:
    js_files = js_file.read().strip().split("\n")

httpx(js_files, project_name)
