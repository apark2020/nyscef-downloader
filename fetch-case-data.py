import requests
import json
import pprint

from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
}

case_data_map = []

with open('cases-09-03.json') as json_file:
    data = json.load(json_file)

    for date, courts in data.items():
        for court_name, cases in courts.items():
            print("Finding cases for {}".format(court_name))
            for case in cases:
                params = (
                    ('docketId', case['docket_id']),
                )
                print("URL: https://iapps.courts.state.ny.us/nyscef/CaseDetails?docketId={}==".format(case["docket_id"]))
                response = requests.get(
                    "https://iapps.courts.state.ny.us/nyscef/CaseDetails?docketId={}==".format(case["docket_id"]),
                    headers=headers, params=params
                )
                soup = BeautifulSoup(response.text, 'html.parser')
                case_summary = soup.find(class_='CaseSummary')
                case_title = case_summary.find(class_='captionText').text
                court = soup.find(class_='PageHeadingDesc').text
                case_id = soup.find('a', class_='skipTo').text
                case_type = case_summary.findAll('span', class_='row')[1].find('strong').text
                case_status = case_summary.findAll('span', class_='row')[2].find('strong').text
                filing_status = case_summary.findAll('span', class_='row')[3].find('strong').text
                try:
                    judge = case_summary.findAll('span', class_='row')[4].find('strong').text
                except IndexError:
                    judge = ''
                plaintiff_data = soup.find('table', attrs={'summary': 'Petitioners in this case'}).find_all('tr')[1:]
                plaintiffs = []
                for plaintiff in plaintiff_data:
                    plaintiff_attr = [p.text.strip() for p in plaintiff.find_all('td')]
                    plaintiffs.append({
                        'name': plaintiff_attr[0],
                        'consented_by': plaintiff_attr[1]
                    })
                defendant_data = soup.find('table', attrs={'summary': 'Respondents in this case'}).find_all('tr')[1:]
                defendants = []
                for defendant in defendant_data:
                    defendant_attr = [d.text.strip() for d in defendant.find_all('td')]
                    defendants.append({
                        'name': defendant_attr[0],
                        'consented_by': defendant_attr[1]
                    })
                case_data = {
                    'url': "https://iapps.courts.state.ny.us/nyscef/CaseDetails?docketId={}==".format(case["docket_id"]),
                    'title': case_title,
                    'court': court,
                    'case_id': case_id,
                    'case_type': case_type,
                    'case_status': case_status,
                    'filing_status': filing_status,
                    'judge': judge,
                    'plaintiffs': plaintiffs,
                    'respondents': defendants,
                    'date': date
                }
                pprint.pprint(case_data)
                case_data_map.append(case_data)

with open('case_data.json', 'w') as f:
    json.dump(case_data_map, f)
