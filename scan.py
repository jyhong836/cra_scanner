# Note to download the page first

# Import the necessary libraries
from bs4 import BeautifulSoup
from collections import defaultdict
import pandas as pd

file_path = 'data/cra_11122023.html'

with open(file_path, 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Find all <li> tags
li_tags = soup.find_all('li', class_='job-type-professional')

def parse_info(li_soup):
    job_info = {
        "title": li_soup.h3.text.strip() if li_soup.h3 else None,
        "company": li_soup.find('div', class_='company').text.strip() if li_soup.find('div', class_='company') else None,
        "location": li_soup.find('div', class_='location').find('strong').text.strip() if li_soup.find('div', class_='location') else None,
        "job_type": li_soup.find('li', class_='job-type').text.strip() if li_soup.find('li', class_='job-type') else None,
        "date_posted": li_soup.find('li', class_='date').text.strip() if li_soup.find('li', class_='date') else None
    }
    return job_info

# Print each list item
df_dict = defaultdict(list)
for li_soup in li_tags:
    job_info = {
        "title": li_soup.h3.text.strip() if li_soup.h3 else None,
        "school": li_soup.find('div', class_='company').text.strip() if li_soup.find('div', class_='company') else None,
        "university": li_soup.find('div', class_='location').find('strong').text.strip() if li_soup.find('div', class_='location') else None,
        "location": list(li_soup.find('div', class_='location'))[-1].strip() if li_soup.find('div', class_='location') else None,
        "job_type": li_soup.find('li', class_='job-type').text.strip() if li_soup.find('li', class_='job-type') else None,
        "date_posted": li_soup.find('li', class_='date').text.strip() if li_soup.find('li', class_='date') else None,
        "link": li_soup.a['href'],
    }
    for k, v in job_info.items():
        df_dict[k].append(v)
    # position_info = li.findAll('div', class_='position')
    # loc_info = li.findAll('div', class_='location')
    # meta_info = li.findAll('div', class_='meta')
    # job_info = parse_info(li)
    # print(li_soup.text)  # Use .text to get the text content of each <li> tag

df = pd.DataFrame(df_dict)
print(df)
df.to_csv(file_path.replace('html', 'csv'))
