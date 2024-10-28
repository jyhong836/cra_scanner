# Note to download the page first
import os
from bs4 import BeautifulSoup
from collections import defaultdict
import pandas as pd
import re
import requests
from datetime import datetime
from utils import get_R1_university
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def extract_and_convert_dates(text):
    # Regular expression to match dates in various formats
    date_patterns = [
        r'\b\d{4}-\d{1,2}-\d{1,2}\b',  # Matches dates in YYYY-MM-DD format
        r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # Matches dates in MM/DD/YYYY format
        r'\b\d{1,2}-\d{1,2}-\d{4}\b',  # Matches dates in DD-MM-YYYY format
        r'\b\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{4}\b', # Matches dates like 12 January 2023
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{1,2},\s\d{4}\b', # Matches dates like January 12, 2023
        r"(?:(?:\d{1,2}/\d{1,2}/\d{2,4})|(?:\d{2,4}/\d{1,2}/\d{1,2})|(?:\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b[\s,]*\d{1,2}[\s,]*\d{2,4})|(?:\d{1,2}[\s]*\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b[\s,]*\d{2,4}))",
    ]

    dates = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            # Try to convert the found date to a datetime object
            # must include day.
            formats = ['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y', '%B %d, %Y', '%d %B %Y', '%B %d %Y']
            for format in formats:
                try:
                    date_obj = datetime.strptime(match, format)
                except ValueError:
                    # print(f"Fail to convert: {match} in {format}")
                    continue
                dates.append(date_obj)
                break
            else:
                print(f"Fail to convert: {match} in any formats.")
    return dates


# file_path = 'data/cra_11122023.html'

def scan_file(file_path, df_dict):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all <li> tags
    li_tags = soup.find_all('div', class_='row record')

    # Print each list item
    for idx, li_soup in enumerate(li_tags):
        job_info = {
            'Position': li_soup.find('a').text.strip(),
            "Institute": li_soup.find('div', class_='col-sm-7').contents[4].strip(),
            "Department": li_soup.find('div', class_='col-sm-5').contents[0].strip(),
            "Location": li_soup.find('div', class_='col-sm-7').contents[-1].strip(),
            "post date": li_soup.find('div', class_='col-sm-5 text-sm-right').contents[2].split(' ')[2].strip(),
            "link": li_soup.find('a')['href'],
        }
        job_info["post date"] = datetime.strptime(job_info["post date"], '%m/%d/%y')
        if job_info["post date"] < datetime.strptime('06/01/23', '%m/%d/%y'):  # too old
            continue
        job_info["post date"] = job_info["post date"].strftime('%m/%d/%Y')
        if any([ex_pos in job_info['Position'].lower() for ex_pos in ['lecturer', 'instructor', 'teaching', 'dean', 'chair', 'postdoc', 'fellow', 'tenured']]):
            continue
        if any([ex_pos in job_info['Location'].lower() for ex_pos in ['china', 'canada', 'hong kong']]):
            continue
        if any([ex_pos in job_info['Department'].lower() for ex_pos in ['biology', 'management', 'law', 'math']]):
            continue
        if job_info['Institute'].strip().lower() not in R1_list:
            print(f" [Not R1] {job_info['Institute']}")
            continue
        if job_info['Institute'] in df_cra['Institute'].values:
            if job_info["Department"] == "Computer Science":
                print(f" [Exist] {job_info['Institute']} has been recorded in CRA.")
                continue
        
        # response = requests.get(job_info['link'])
        # job_html_content = response.content
        # job_soup = BeautifulSoup(job_html_content, 'html.parser')
        # job_desc = job_soup.find('div', class_="jobDesc").text
        
        
        # # Go to the webpage
        # time.sleep(5)
        # driver.get(job_info['link'])

        # # Wait for an element to load
        # element = WebDriverWait(driver, 1000).until(
        #     EC.presence_of_element_located((By.ID, 'jobDesc'))
        # )
        # # Extract the data
        # job_desc = element.text
        
        # dates = extract_and_convert_dates(job_desc)
        # # dates = re.findall(date_pattern, job_desc)
        # if len(dates) > 0:
        #     # print([d.strftime('%m/%d/%Y') for d in dates])
        #     print(f'[{idx}/{len(li_tags)}] earliest date', min(dates).strftime('%m/%d/%Y'))
        #     job_info['due'] = min(dates).strftime('%m/%d/%Y')
        # else:
        #     job_info['due'] = ''
        
        for k, v in job_info.items():
            df_dict[k].append(v)

R1_list = get_R1_university()
R1_list = [u.strip().lower() for u in R1_list]

driver_path = 'chromedriver/chromedriver'

# Create a new instance of the browser
driver = webdriver.Chrome(driver_path)


df_cra = pd.read_csv('data/cra_11122023.csv')

df_dict = defaultdict(list)
high_dir = 'data/highered_11122023'
files = os.listdir(high_dir)
for file_name in files:
    if file_name.startswith('.'):
        continue
    file_path = os.path.join(high_dir, file_name)
    print(f"\nscan file: {file_path}")
    scan_file(file_path, df_dict)

df = pd.DataFrame(df_dict)
print(df)
df.to_csv(high_dir + '.csv')
