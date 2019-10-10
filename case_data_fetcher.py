import argparse
import json
import requests
import sys

from bs4 import BeautifulSoup

BASE_DOCKET_SEARCH_URL = "https://iapps.courts.state.ny.us/nyscef/CaseDetails?docketId="


def get_case_summary_data(soup):
    case_summary = soup.find(class_='CaseSummary')
    if not case_summary:
        print('something went wrong')
        return {}
    case_title = case_summary.find(class_='captionText').text
    court = soup.find(class_='PageHeadingDesc').text
    case_id = soup.find('a', class_='skipTo').text
    case_type = case_summary.findAll('span', class_='row')[1].find('strong').text
    case_status = case_summary.findAll('span', class_='row')[2].find('strong').text
    filing_status = case_summary.findAll('span', class_='row')[3].find('strong').text
    judge = None
    try:
        judge = case_summary.findAll('span', class_='row')[4].find('strong').text
    except IndexError:
        pass

    return {
        'title': case_title,
        'court': court,
        'case_id': case_id,
        'case_type': case_type,
        'case_status': case_status,
        'filing_status': filing_status,
        'judge': judge
    }


def format_names(data):
    if data == 'none recorded':
        return None
    else:
        return list(filter(None, [' '.join(a.split()) for a in data.split("\n")]))


def get_arbiter_data(soup, arbiter_type):
    try:
        arbiter_data = soup.find(
            'table', attrs={'summary': '{}s in this case'.format(arbiter_type)}
        ).find_all('tr')[1:]
    except AttributeError:
        return {}
    arbiters = []
    for arbiter in arbiter_data:
        arbiter_attr = [p.text.strip() for p in arbiter.find_all('td')]
        if arbiter_attr:
            name = format_names(arbiter_attr[0])
            consented_by = format_names(arbiter_attr[1])
            arbiters.append({
                'name': name,
                'consented_by': consented_by
            })

    return {arbiter_type.lower(): arbiters}


def main(docket_ids, output_file):
    case_data = []
    for docket_id in docket_ids:
        request_headers = {"User-Agent": ""}
        request_params = (('docketId', docket_id),)
        request_url = BASE_DOCKET_SEARCH_URL + docket_id + "=="
        response = requests.get(
            request_url,
            headers=request_headers,
            params=request_params
        )
        soup = BeautifulSoup(response.text, 'html.parser')
        summary_data = get_case_summary_data(soup)
        petitioner_data = get_arbiter_data(soup, arbiter_type='Petitioner')
        respondent_data = get_arbiter_data(soup, arbiter_type='Respondent')
        summary_data.update(petitioner_data)
        summary_data.update(respondent_data)
        case_data.append(summary_data)

    print(case_data)
    with open(output_file, 'w') as f:
        json.dump(case_data, f)


if __name__ == '__main__':
    cl = argparse.ArgumentParser(description="This script finds docket ids on NYSCEF.")
    cl.add_argument("--docket-ids", help="a list of docket ids")
    cl.add_argument("--docket-ids-file", default='ids.txt', help="the location with docket ids")
    cl.add_argument("--output", default='case_data.json', help="the output file location")
    args = cl.parse_args()

    if args.docket_ids:
        docket_ids = args.docket_ids.split(",")
    else:
        with open(args.docket_ids_file) as f:
            docket_ids = f.readlines()

    sys.exit(main(docket_ids, args.output))
