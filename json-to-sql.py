import sqlite3
import json

conn = sqlite3.connect('test.db')


c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS cases (id varchar(3), data json)")

with open('case_data.json') as json_file:
    data = json.load(json_file)

for case in data:
    c.execute("insert into cases values (?, ?)", [case['title'], )
    c.execute("insert into cases values (?, ?)", [case['court'], )
    c.execute("insert into cases values (?, ?)", [case['case_id'], )
    c.execute("insert into cases values (?, ?)", [case['case_type'], )
    c.execute("insert into cases values (?, ?)", [case['case_status'], )
    c.execute("insert into cases values (?, ?)", [case['filing_status'], )
    conn.commit()

# Close db connection
conn.close()
