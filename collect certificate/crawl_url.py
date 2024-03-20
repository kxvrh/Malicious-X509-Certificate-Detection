from bs4 import BeautifulSoup
import requests
import time
import helper

PHISH_URL_LIST = 'https://phishtank.org/phish_search.php?page=@page@&active=y&verified=u'
PHISH_DETAIL_URL = 'https://phishtank.org/phish_detail.php?phish_id=@id@'
phish_url_list = []
phish_url_id = []



def get_html(page_url):
    response = requests.Response()
    rate_limited = -1
    try:
        response = requests.get(page_url, timeout=1)
        rate_limited = response.text.find('You have exceeded the number of allowed requests. Please try again shortly.')
    except Exception as e:
        print(e)
    
    # limited access
    while (rate_limited != -1 or response == None):
        time.sleep(10)
        try:
           response = requests.get(page_url, timeout=1)
           rate_limited = response.text.find('You have exceeded the number of allowed requests. Please try again shortly.')
        except Exception as e:
            print(e)
        
    return response.text


def get_url_from_id(id):
    # extract phish url from phishtank by id
    req = PHISH_DETAIL_URL.replace('@id@', str(id))
    html = get_html(req)
    list_soup = BeautifulSoup(html, 'html.parser')
    span = list_soup.find('span', {'style': 'word-wrap:break-word;'})
    if span == None:
        print(f'Could not get url from id: {id}')
        return None
    url = str(span.contents[0]).replace('<b>','').replace('</b>', '')
    return url


def get_url_from_html(html):
    # extract phish url by parsing html from phishtank
    list_soup = BeautifulSoup(html, 'html.parser')

    table = list_soup.find('table', {'class': 'data'})
    rows = table.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if len(cells) == 0:
            continue
        phish_id = cells[0].contents[0].text
        phish_url = cells[1].contents[0].text
        
        if '...' in phish_url:
            phish_url = get_url_from_id(phish_id)
        # print(phish_url)
        if phish_url != None:
            phish_url_list.append(phish_url)
            phish_url_id.append(phish_id)


def traverse_page(page, index):
   page_url = page.replace('@page@', str(index))
   html = get_html(page_url)
   if html:
       get_url_from_html(html)
               

if __name__ == '__main__':
    '''
    extract phish url from phishtank
    '''
    for index in range(0,400):
        traverse_page(PHISH_URL_LIST, index)
    helper.save_url(phish_url_id, phish_url_list)