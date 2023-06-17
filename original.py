import socket
import urllib.parse
import subprocess
try:import requests
except ImportError:
    subprocess.call(['pip', 'install', 'requests'])
import requests
try:import shodan
except ImportError:
    subprocess.call(['pip', 'install', 'shodan'])
import shodan
try:import whois
except ImportError:
    subprocess.call(['pip', 'install', 'python-whois'])
import whois
try:import bs4
except ImportError:
    subprocess.call(['pip', 'install', 'beautifulsoup4'])
from bs4 import BeautifulSoup
try:import easygui
except ImportError:
    subprocess.call(['pip', 'install', 'easygui'])
import easygui

titlescreen = """
\033[1;31;40m  ,---.   ,-----.  ,---.          ,-----.  ,---.  ,--.,--.  ,--.,--------.
\033[1;31;40m /  O  \ '  .--./ /  O  \ ,-----.'  .-.  ''   .-' |  ||  ,'.|  |'--.  .--'
\033[1;37;40m|  .-.  ||  |    |  .-.  |'-----'|  | |  |`.  `-. |  ||  |' '  |   |  |
\033[1;34;40m|  | |  |'  '--'\|  | |  |       '  '-'  '.-'    ||  ||  | `   |   |  |
\033[1;34;40m`--' `--' `-----'`--' `--'        `-----' `-----' `--'`--'  `--'   `--'\033[0m
"""
print(titlescreen)

# target popup
target = easygui.enterbox("Enter the website URL: ")

# Target
url = target
parsed_url = urllib.parse.urlparse("https://" + url)
domain_name = parsed_url.netloc

# IP
ip_address = socket.gethostbyname(domain_name)
print(f"\nIP Address: {ip_address}")

# WHOIS
domain_info = whois.whois(domain_name)

# DNS
print(f"DNS Information:")
dns_entries = domain_info.name_servers
for dns in dns_entries:
    print(f"\t{dns}")

# Crawler
page = requests.get("https://" + url)
soup = BeautifulSoup(page.content, 'html.parser')
emails = set()
usernames = set()
for link in soup.find_all('a'):
    href = link.get('href')
    if href is not None and ('mailto:' in href):
        email = href.split(':')[-1]
        emails.add(email)
    elif href is not None and ('twitter.com/' in href or 'instagram.com/' in href):
        username = href.split('/')[-1]
        usernames.add(username)

# Emails & usernames
if emails:
    print("Emails:")
    for email in emails:
        print(f"\t{email}")
else: print("No emails found on the webpage.")

if usernames:
    print("Usernames:")
    for username in usernames:
        print(f"\t{username}")
else: print("No usernames found on the webpage.")

print(f"all hyperlinks found:\t")
for link in soup.find_all('a'):
    href = link.get('href')
    if href is not None and ('http' in href):print(f"\t{href}")

# Wayback Machine
wayback_json = f"http://archive.org/wayback/available?url={url}"
response = requests.get(wayback_json)
data = response.json()
    # Check if snapshots are saved
if 'closest' not in data['archived_snapshots']:
    print(f"The target '{url}' is not in the Wayback Machine")
else:
    # Scrape the number of snapshots found
    page2 = requests.get("http://web.archive.org/cdx/search/cdx?url=" + url + "&output=json")
    soup2 = BeautifulSoup(page2.content, 'html.parser')
    x = page2.text.count(url)
    print(f"\nNumber of snapshots found: {x}")
    # Get the URL of the most recent archived snapshot
    snapshot_url = data['archived_snapshots']['closest']['url']
    print(f"Most recent snapshot: {snapshot_url}")
