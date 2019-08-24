from datetime import timedelta, date
import json
import re
import requests
from subprocess import check_output

from bs4 import BeautifulSoup
import pytesseract
from PIL import Image

NEW_YORK_COUNTY_COURTS = {
    "Albany": "25",
    "Bronx": "119",
    "Broome": "100",
    "Cattaraugus": "6420087",
    "Cayuga": "641962",
    "Chautauqua": "4667226",
    "Chemung": "6822102",
    "Chenango": "5125702",
    "Cortland": "1651522",
    "Delaware": "5531322",
    "Dutchess": "1703419",
    "Erie": "30",
    "Essex": "105",
    "Franklin": "5986392",
    "Genesee": "5985121",
    "Jefferson": "5125764",
    "Kings": "29",
    "Lewis": "51257",
    "Litigation Coordinating Panel": "7169955",
    "Livingston": "120",
    "Madison": "5531569",
    "Monroe": "4",
    "Nassau": "26",
    "New York": "3",
    "Niagara": "108",
    "Oneida": "317574",
    "Onondaga": "111",
    "Ontario": "2265404",
    "Orange": "317349",
    "Oswego": "408019",
    "Otsego": "553194",
    "Putnam": "382808",
    "Queens": "114",
    "Richmond": "115",
    "Rockland": "608923",
    "Schuyler": "6822296",
    "Seneca": "512585",
    "St. Lawrence": "5985660",
    "Steuben": "4667399",
    "Suffolk": "27",
    "Sullivan": "116",
    "Tioga": "55317",
    "Tompkins": "608924",
    "Warren": "553211",
    "Washington": "5532300",
    "Wayne": "51258",
    "Westchester": "2",
    "Yates": "64191"
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36', # noqa
}


params = (
    ('TAB', 'courtDateRange'),
)

data = {
  'btnSubmit': 'Search'
}

case_data = {}


def resolve(path):
    check_output(['convert', path, '-resample', '600', path])
    return pytesseract.image_to_string(Image.open(path))


def get_new_session_id():
    page_response = requests.get(
        'https://iapps.courts.state.ny.us/nyscef/CaseSearch',
        headers=headers
    )
    soup = BeautifulSoup(page_response.text, 'html.parser')
    img = soup.find('img')['src']
    img_request = requests.get(
        "{}/{}".format("https://iapps.courts.state.ny.us/nyscef", img),
        headers=headers
    )
    print(img_request)
    open('captcha.jpg', 'wb').write(img_request.content)
    captcha_text = resolve('captcha.jpg')

    captcha_data = {'jcaptcha_answer': captcha_text}
    response = requests.post(
        'https://iapps.courts.state.ny.us/nyscef/CaseSearch',
        headers=headers,
        data=captcha_data
    )

    return response


request_count = 0
print('start with a session id:')
session_id = get_new_session_id()
cookies = {
    'JSESSIONID': session_id
}


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


start_date = date(2019, 8, 14)
end_date = date()

for filing_date in daterange(start_date, end_date):
    filing_date = filing_date.strftime("%m-%d-%Y")
    print("Starting with filing date {}".format(filing_date))
    case_data[filing_date] = {}
    data['txtFilingDate'] = filing_date
    for court, court_id in NEW_YORK_COUNTY_COURTS.items():
        case_data[filing_date][court] = []
        print("starting court: {}".format(court))
        print("Current request count: {}".format(request_count))
        data['selCountyCourt'] = court_id
        initial_response = requests.post(
            'https://iapps.courts.state.ny.us/nyscef/CaseSearch?PageNum=1',
            headers=headers, params=params, cookies=cookies, data=data)
        request_count += 1
        if request_count > 60:
            print("need session id for a search on {}".format(court))
            cookies['JSESSIONID'] = get_new_session_id()
            request_count = 0
        soup = BeautifulSoup(initial_response.text, 'html.parser')
        if soup.find(class_="MsgBox_Error"):
            print("AN ERROR OCCURRED")
            print(soup.find("span", class_="MsgBox_Message").text.strip())
        try:
            last_page = [
                a.get('href') for a in soup.find('span', class_='pageNumbers')
                .findAll('a')
            ][-1]
            pages_num = int(last_page.split('?PageNum=')[-1])
            print('pages: {}'.format(pages_num))
        except AttributeError:
            pages_num = 1

        docket_ids = []
        for i in range(0, pages_num):
            params = (('PageNum', str(i + 1)),)
            page_response = requests.get(
                'https://iapps.courts.state.ny.us/nyscef/CaseSearchResults',
                headers=headers, params=params, cookies=cookies
            )
            soup = BeautifulSoup(page_response.text, 'html.parser')
            request_count += 1
            rows = soup.findAll('tr')
            for r in rows:
                table_data = r.findAll('td')
                if table_data:
                    link = table_data[0]
                    case_status = table_data[1]
                    case_title = table_data[2]
                    case_type = table_data[3]
                    if 'Torts - Child Victims Act' in case_type.text:
                        url = link.findAll('a')[0].get('href')
                        docket_id = re.search(r'(?:docketId)=(.*)(?:==)', url).group(0).replace('docketId=', '').replace('==', '') # noqa
                        case_data[filing_date][court].append({
                            'docket_id': docket_id,
                            'case_status': case_status.text,
                            'case_type': case_type.text,
                            'case_title': case_title.text
                        })
                        with open("ids.txt", "a") as ids_file:
                            ids_file.write(docket_id)
                            ids_file.write("\n")


with open('cases.json', 'w') as f:
    json.dump(case_data, f)
