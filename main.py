from flask import Flask, request
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from tabulate import tabulate
import json

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/process')
def process_data():
    current_month = datetime.now().strftime("%B").lower()
    current_year = datetime.now().strftime("%Y")

    try:
        url = f"https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/{current_year}/visa-bulletin-for-{current_month}-{current_year}.html"
        response = requests.get(url)
        response.raise_for_status()
        print(url)

    except requests.HTTPError as e:
        print(f"HTTP Error: {e}")
        
        if current_month in ["october", "november", "december"]:
            next_year = str(int(current_year) + 1)
            url = f"https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/{next_year}/visa-bulletin-for-{current_month}-{current_year}.html"
            print(url)
        else:
            previous_month_date = datetime.now() - timedelta(days=30)
            previous_month = previous_month_date.strftime("%B").lower()
            url = f"https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/{current_year}/visa-bulletin-for-{previous_month}-{current_year}.html"
            print(url)

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.HTTPError as e:
            return f"Failed to fetch data. Error: {e}"

    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    target_table_name = "Table 8"
    tables = soup.find_all("table")

    for table_index, table in enumerate(tables):
        table_data = []
        for row in table.find_all("tr"):
            row_data = []
            for cell in row.find_all(["td", "th"]):
                row_data.append(cell.text.strip())
            table_data.append(row_data)

        if f"Table {table_index + 1}" == target_table_name:
            table_data[0] = [cell.replace('\n', '').replace('\xa0', '') for cell in table_data[0]]
            headers = table_data[0]
            print('----------------------------------------')
            print(headers)
            for row in table_data:
                print(row)     
            print('-----------------------------------------------------------')  
            print ('  ')
            new_data = []
            new_data= [[cell.replace('\n', '').replace('\xa0', '') for cell in row] for row in table_data]
            for row in new_data:
                print(row)
            print('------------------------------------------------------------')
            json_data = [dict(zip(headers, row)) for row in  new_data[1:]]
            print(json_data)
            json_str = json.dumps(json_data, indent=4)
            print(json_str)
            return json_str

    return "Table not found in the page."

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug =  True)
