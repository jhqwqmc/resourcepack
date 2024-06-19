import requests
from urllib.parse import urlparse, parse_qs

def get_download_url(_url):
    session = requests.Session()
    response = session.get(_url)
    parsed_url = urlparse(response.url)
    params = parse_qs(parsed_url.query)
    download_url = f"https://api.onedrive.com/v1.0/drives/{params['cid'][0]}/items/{params['id'][0]}?select=id%2C%40content.downloadUrl&authkey={params['authkey'][0]}"
    response = session.get(download_url).json()
    
    return response['@content.downloadUrl']

print(get_download_url("https://1drv.ms/u/s!AhWb6SjLj2axiZgrTLMFyzFOE_JEiA?e=BTdsIz"))