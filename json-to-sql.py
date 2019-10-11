import sqlite3
import json

conn = sqlite3.connect('child_victims_act_data.db')
c = conn.cursor()
c.execute('''CREATE TABLE cases(title text, court text, case_id text, case_type text, case_status text, filing_status text, judge text)''')
c.execute('''CREATE TABLE arbiters(case_id text, arbiter_type text,  names text, consented_by text)''')
c.execute('''CREATE TABLE documents(case_id text, title text, link text, filed_by text, filed_date text, received_date text, confirmation_link text, confirmation_state text)''')

with open('case_data.json') as json_file:
    data = json.load(json_file)

for case in data:
    if not case.get('title'):
        continue
    title = case['title']
    court = case['court']
    case_id = case['case_id']
    case_type = case['case_type']
    case_status = case['case_status']
    filing_status = case['filing_status']
    judge = case['judge']
    respondents = case['respondents']
    petitioners = case['petitioners']
    documents = case['documents']
    c.execute("INSERT INTO cases VALUES (?, ?, ?, ?, ?, ?, ?)", (title, court, case_id, case_type, case_status, filing_status, judge))

    for respondent in respondents:
        aribter_type = 'respondent'
        names = str(respondent['name'])
        consented_by = str(respondent['consented_by'])
        c.execute("INSERT INTO arbiters VALUES (?, ?, ?, ?)", (case_id, aribter_type, names, consented_by))

    for petitioner in petitioners:
        aribter_type = 'petitioner'
        names = str(petitioner['name'])
        consented_by = str(petitioner['consented_by'])
        c.execute("INSERT INTO arbiters VALUES (?, ?, ?, ?)", (case_id, aribter_type, names, consented_by))

    for document in documents:
        document_title = document['title']
        link = document['link']
        filed_by = document['filed_by']
        filed_date = document['filed_date']
        received_date = document['received_date']
        confirmation_link = document['confirmation_link']
        confirmation_state = document['confirmation_state']
        c.execute("INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (case_id, document_title, link, filed_by, filed_date, received_date, confirmation_link, confirmation_state))

    conn.commit()

# Close db connection
conn.close()
