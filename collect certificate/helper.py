import socket
import requests
from urllib import parse, request
import os
import pandas as pd

CRTSH_URL = "https://crt.sh/?d="


def is_port_open(host, port=443):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.settimeout(10)
    res = conn.connect_ex((host, port))   # return 0 if connected
    is_open = not bool (res)
    if not is_open:
        print(f'Port {port} is closed for {host}')
    return is_open


def get_ip_from_url(url):
    domain = url.replace('http://', '').replace('https://', '').replace('/', '')
    try:
        info = socket.getaddrinfo(domain, 80, 0, 0, socket.SOL_TCP)
        return info[0][4][0]
    except Exception as e:
        print(e)
        return None
    

def get_fqdn_from_url(url):
    res = parse.urlparse(url)
    netloc = res.netloc
    if ':' in netloc:
        netloc =  netloc.split(':')[0]
    return netloc


def get_cert_from_id(crt_id):
    # get cert, pem, response code from crt.sh by id
    from asn1crypto import pem, x509
    url = CRTSH_URL + str(crt_id)
    response = request.urlopen(url)
    txt = response.read()              # pem
    error = response.status_code
    try:
        der_bytes = pem.unarmor(txt.encode('utf-8'))[2]
        cert = x509.Certificate.load(der_bytes)
    except:
        print(f'Could not get cert for id {crt_id} : error {error}')
        return None, None, None
    return cert, txt, response.status_code


def get_data_from_api(api):
    # need phishtank's api
    from fake_useragent import UserAgent
    ua = UserAgent()
    f_headers = {'User-Agent': ua.random}
    url = f"http://data.phishtank.com/data/{api}/online-valid.csv"
    page = requests.get(url, headers=f_headers)
    print(page.status_code)
    contents = page.text
    with open('content.txt', 'w+') as f:
        f.write(contents)


def save_url(id_list, url_list, path=os.getcwd(), filename='url.csv'):
    pd.DataFrame({"id":id_list, "url":url_list}).to_csv(path+'/'+filename, header = True, index = True, sep = ",")


