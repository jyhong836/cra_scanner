from bs4 import BeautifulSoup
import csv

# Load HTML content from a file
with open('data/csrankings.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Find all table rows in the tbody
rows = soup.select('tbody')[0]

# Extract university names
university_names = []
for row in rows:
    try:
        # The university name is in the second 'td' element with a span containing the text
        university_name = row.find_all('td')[1].find_all(
            'span', recursive=False)[1].text.strip()
        university_names.append(university_name)
    except:
        continue

# Output the result
print("Found ", len(university_names))
# Specify the filename
filename = "data/csrankings.csv"

# Write the list to a CSV file
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    # Writing each university name in a new row
    for university in university_names:
        writer.writerow([university])

print(f"List saved to {filename}")
