import requests
import os
import sys

from bs4 import BeautifulSoup
from urllib.parse import urljoin , urlparse

def get_domain(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if ":" in domain:
        domain = domain.split(":")[0]
    return domain


def download_static_files(url):
    domain = get_domain(url)
    
    # Get the HTML content of the page
    response = requests.get(url)
    
    html = response.content

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Get all static files on the page
    static_files = []
    for tag in soup.find_all():
        for attribute in ['src', 'href']:
            attr = tag.get(attribute)
            if attr:
                if attr.startswith('//'):
                    attr = 'http:' + attr
                elif not attr.startswith(('http', 'https', 'ftp')):
                    attr = urljoin(url, attr)
                parsed_url = urlparse(attr)
                if os.path.splitext(parsed_url.path)[1] not in ['.html', '.php', '.asp']:
                    static_files.append(attr)

    # Download all static files
    for file_url in static_files:
        # Get the filename and file path
        parsed_url = urlparse(file_url)
        file_path = os.path.join(parsed_url.netloc, parsed_url.path[1:])
        
        if  domain in file_path:
            # Make sure the directory exists
            dir_path = os.path.dirname(file_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            with open(domain + "/index.html", 'wb') as f:
                    f.write(html)
            
            # Download the file
            print(f'Downloading {file_url} to {file_path}...')
            try:
                response = requests.get(file_url)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
            except Exception as e:
                print(f'Error downloading {file_url}: {e}')

if len(sys.argv) != 2:
    print("Error!! Usage: python3 app.py <url>")
    sys.exit()

url=sys.argv[1]

# Example usage:
download_static_files(url)

domain = get_domain(url)

os.system("cd " + domain +  " &&  python3 -m http.server" )
