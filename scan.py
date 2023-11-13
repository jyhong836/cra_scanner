# Note to download the page first

# Import the necessary libraries
from bs4 import BeautifulSoup
from collections import defaultdict
import pandas as pd
import re
import requests
from datetime import datetime

file_path = 'data/cra_11122023.html'

with open(file_path, 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Find all <li> tags
li_tags = soup.find_all('li', class_='job-type-professional')

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
            # try:
            #     # Different formats require different parsing methods
            #     if '-' in match and match.count('-') == 2:
            #         # ISO format (YYYY-MM-DD)
            #         date_obj = datetime.strptime(match, '%Y-%m-%d')
            #     elif '/' in match:
            #         # US format (MM/DD/YYYY)
            #         date_obj = datetime.strptime(match, '%m/%d/%Y')
            #     elif '-' in match:
            #         # European format (DD-MM-YYYY)
            #         date_obj = datetime.strptime(match, '%d-%m-%Y')
            #     elif ',' in match:
            #         # Format like January 12, 2023
            #         date_obj = datetime.strptime(match, '%B %d, %Y')
            #     else:
            #         # Format like 12 January 2023
            #         date_obj = datetime.strptime(match, '%d %B %Y')

            #     dates.append(date_obj)
            # except ValueError:
            #     # pass  # If the conversion fails, skip the date
            #     print(f"Fail to convert: {match}")

    return dates

# Print each list item
df_dict = defaultdict(list)
for idx, li_soup in enumerate(li_tags):
    job_info = {
        "Position": li_soup.h3.text.strip() if li_soup.h3 else None,
        "Department": li_soup.find('div', class_='company').text.strip() if li_soup.find('div', class_='company') else None,
        "Institute": li_soup.find('div', class_='location').find('strong').text.strip() if li_soup.find('div', class_='location') else None,
        "location": list(li_soup.find('div', class_='location'))[-1].strip() if li_soup.find('div', class_='location') else None,
        # "job_type": li_soup.find('li', class_='job-type').text.strip() if li_soup.find('li', class_='job-type') else None,
        # "date_posted": li_soup.find('li', class_='date').text.strip() if li_soup.find('li', class_='date') else None,
        "link": li_soup.a['href'],
    }
    # position_info = li.findAll('div', class_='position')
    # loc_info = li.findAll('div', class_='location')
    # meta_info = li.findAll('div', class_='meta')
    # job_info = parse_info(li)
    # print(li_soup.text)  # Use .text to get the text content of each <li> tag
    
    # date_pattern = r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)?\b[\s/-]*(?:\d{1,2}[\s/-]*)?\d{4}|\d{1,2}/\d{1,2}/\d{2,4}"
    
    response = requests.get(li_soup.a['href'])
    job_html_content = response.content
    job_soup = BeautifulSoup(job_html_content, 'html.parser')
    job_desc = job_soup.find('div', class_="job_description").text
    # date_pattern = r"(?:(?:\d{1,2}/\d{1,2}/\d{2,4})|(?:\d{2,4}/\d{1,2}/\d{1,2})|(?:\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b[\s,]*\d{1,2}[\s,]*\d{2,4})|(?:\d{1,2}[\s]*\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b[\s,]*\d{2,4}))"
    dates = extract_and_convert_dates(job_desc)
    # dates = re.findall(date_pattern, job_desc)
    if len(dates) > 0:
        # print([d.strftime('%m/%d/%Y') for d in dates])
        print(f'[{idx}/{len(li_tags)}] earliest date', min(dates).strftime('%m/%d/%Y'))
        job_info['due'] = min(dates).strftime('%m/%d/%Y')
    else:
        job_info['due'] = ''
    
    for k, v in job_info.items():
        df_dict[k].append(v)

df = pd.DataFrame(df_dict)
print(df)
df.to_csv(file_path.replace('html', 'csv'))
