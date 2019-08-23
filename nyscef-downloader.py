import requests
from bs4 import BeautifulSoup

NEW_YORK_COUNTY_COURTS = [
    "Albany County Supreme Court",
    "Bronx County Supreme Court",
    "Broome County Supreme Court",
    "Cattaraugus County Supreme Court",
    "Cayuga County Supreme Court",
    "Chautauqua County Supreme Court",
    "Chemung County Supreme Court",
    "Chenango County Supreme Court",
    "Cortland County Supreme Court",
    "Delaware County Supreme Court",
    "Dutchess County Supreme Court",
    "Erie County Supreme Court",
    "Essex County Supreme Court",
    "Franklin County Supreme Court",
    "Genesee County Supreme Court",
    "Jefferson County Supreme Court",
    "Kings County Supreme Court",
    "Lewis County Supreme Court",
    "Litigation Coordinating Panel",
    "Livingston County Supreme Court",
    "Madison County Supreme Court",
    "Monroe County Supreme Court",
    "Nassau County Supreme Court",
    "New York County Supreme Court",
    "Niagara County Supreme Court",
    "Oneida County Supreme Court",
    "Onondaga County Supreme Court",
    "Ontario County Supreme Court",
    "Orange County Supreme Court",
    "Oswego County Supreme Court",
    "Otsego County Supreme Court",
    "Putnam County Supreme Court",
    "Queens County Supreme Court",
    "Richmond County Supreme Court",
    "Rockland County Supreme Court",
    "Schuyler County Supreme Court",
    "Seneca County Supreme Court",
    "St. Lawrence County Supreme Court",
    "Steuben County Supreme Court",
    "Suffolk County Supreme Court",
    "Sullivan County Supreme Court",
    "Tioga County Supreme Court",
    "Tompkins County Supreme Court",
    "Warren County Supreme Court",
    "Washington County Supreme Court",
    "Wayne County Supreme Court",
    "Westchester County Supreme Court",
    "Yates County Supreme Court"
]

cookies = {
    'JSESSIONID': '895434A592D2576DB174A1C74260F7B5.server20164',
    'TS01ab7d00': '01084fa67846d52abf4ffa09d0042528e8d191275d9c188fb8096e60bb621b57bef872cadd77640ccbea78fd9a140fe9c1f187c692ee9ec06597ee3ac98b605eaecc8a8cff',
    'ucs_nyscef': 'U0qCZO0vUtepH2nYavubK_PLUS_DaZilg8xDw5zuT0iWO4nA%3D',
    'TS010e0f15': '01084fa67836416d07bbc66dd8752b08cb80b590f2979d8aad73c16048b1678114cb1619231f3b6a4102fa0ce6745747cc2e5db0b476b082ebf5f480f530e804b114ca7ad0',
    'TS010e0f15_77': '08b9a1dceaab2800b168525d099918344d07c7e229ddc5e3ad27c943b113f2c96f1cf0155e8c3b79cafe1ad8c35bd14d082af21951824000028e20666d66bf02bbd7df11802a2987c0ada25d0b011eca304208f2465219e6045e4f4d85799018315ddb7785adf25ce098003707008b1bcb064f70e1fd75fa',
}

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Sec-Fetch-Site': 'none',
    'Referer': 'https://iapps.courts.state.ny.us/nyscef/CaseSearch?TAB=courtDateRange',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
}

response = requests.get('https://iapps.courts.state.ny.us/nyscef/CaseSearchResults', headers=headers, cookies=cookies)
soup = BeautifulSoup(response.text, 'html.parser')

pages = [a.text for a in soup.find('span', class_='pageNumbers').findAll('a')][0:-2]
pages_num = max([int(p) for p in pages])
cases = []

for i in range(1, pages_num):
    urls = [str(a.get('href')) for a in soup.find_all('a')]
    [cases.append(u for u in urls if 'docketId' in u)]
