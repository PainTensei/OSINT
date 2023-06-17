#!/usr/bin/env python
import subprocess
packages = ['requests', 'shodan', 'flask', 'python-whois', 'beautifulsoup4', 'easygui']
for package in packages:
    try:
        __import__(package)
    except ImportError:
        subprocess.call(['pip', 'install', package])
import socket
import json
import urllib.parse
import requests
import shodan
import flask
import whois
import easygui
from bs4 import BeautifulSoup
from flask import Flask, request, render_template_string

app = Flask(__name__)
app.debug = True

@app.route('/')
def dashboard():
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
    
    # location
    print(f"Location:")
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    location_data = {
        "City": response.get("city"),
        "Region": response.get("region"),
        "Country": response.get("country_name")}
    print(f"\t{location_data}")

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
    else:
        print("No emails found on the webpage.")

    if usernames:
        print("Usernames:")
        for username in usernames:
            print(f"\t{username}")
    else:
        print("No usernames found on the webpage.")

    print(f"all hyperlinks found:\t")
    hyperlinks = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href is not None and ('http' in href):
            print(f"\t{href}")
            hyperlinks.append(href)

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

    # Push data to localhost
    data_to_push = {
        'ip_address': ip_address,
        'Target': domain_name,
        'Location': location_data,
        'DNS': dns_entries,
        'emails': list(emails),
        'hyperlinks': hyperlinks,
        'usernames': list(usernames),
        'Latest snapshot': snapshot_url,
        'Number of snapshots': x}
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <meta charset='utf-8'>
    <meta http-equiv='X-UA-Compatible' content='IE=edge'>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <title>Dashboard</title>
    <link href="https://www.aca-it.nl/wp-content/themes/aca-it/favicon.png" rel="icon">
    <style>
    body {
    min-height: 100vh;
    background-image:
    linear-gradient(#1C2833, #212F3D
    );

    }
    * {
    font-family: 'Segoe UI', Tahoma, Verdana, sans-serif;
    }
    .box {
    margin: 1%;
    width: fit-content;
    height: fit-content;
    border: 1px solid #ee2a24;
    background-color: #2C3E50;
    box-shadow: 10px 5px 5px black;
    align-items: center;
    border-radius: 2rem;
    padding: 1.5rem;
    }
    .wrapper {
    display: inline-flex;
    flex-wrap: wrap;
    }
    p, li, ul {
    color: white;
    }
    h2 {
    color: bisque;
    }
    a {
    color: gold;
    }
    h1 {
    margin-left: 1%;
    color: bisque;
    text-shadow: 2px 2px 2px black, 0 0 1em black, 0 0 0.2em black;
    }
    </style>
</head>
<body>
<h1><img style="margin-left: 1%; margin-top: 1%;" width="150px" height="65px" src="https://www.aca-it.nl/wp-content/themes/aca-it/resources/images/svg/logo.svg" alt="main-logo" class="main-logo" loading="lazy">OSINT Information</h1>
<hr>
    <div class="wrapper">
        <div class="box">
            <h2>Target URL</h2>
            <p><a target="_blank" href="https://{{ data['Target'] }}">{{ data['Target'] }}</a></p>
        </div>

        <div class="box">
            <h2>IP address</h2>
            <p>{{ data['ip_address'] }}</p>
        </div>

        <div class="box">
            <h2>DNS Information</h2>
            <ul>
                {% for dns_entry in data['DNS'] %}
                    <li>{{ dns_entry }}</li>
                {% endfor %}
            </ul>
        </div>
        <div class="box">
            <h2>Hyperlinks</h2>
            <ul>
                {% for hyperlinks in data['hyperlinks'] %}
                    <li>{{ hyperlinks }}</li>
                {% endfor %}
            </ul>
        </div>

        <div class="box">
            <h2>Number of Snapshots</h2>
            <p style="font-size: xxx-large; font-weight: bolder;">{{ data['Number of snapshots'] }}</p>
        </div>

        <div class="box">
            <h2>Latest Snapshot</h2>
            <p><a target="_blank" href="{{ data['Latest snapshot'] }}">{{ data['Latest snapshot'] }}</a></p>
        </div>

        <div class="box">
            <h2>Location</h2>
            <iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2485.5244548754!2d5.472948212515854!3d51.46688701354419!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x47c6d9217ea6d109%3A0xd7e03cd66dd3d7cd!2sWooninc.!5e0!3m2!1sen!2snl!4v1685409470783!5m2!1sen!2snl" width="300" height="300" style="border:1;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
    </div>
</body>
</html>
    ''', data=data_to_push)

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000, threaded=False)

# In order to embed correct locations with google maps, you need an API key.
#
# Use https://ipapi.co/{ip}/json/ to find location
#
# <iframe
#   width="450"
#   height="250"
#   frameborder="0" style="border:0"
#   referrerpolicy="no-referrer-when-downgrade"
#   src="https://www.google.com/maps/embed/v1/view?key=API_KEY_HERE&center=-33.8569,151.2152&zoom=12&maptype=satellite"
#   allowfullscreen>
# </iframe>