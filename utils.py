import requests
from bs4 import BeautifulSoup

def get_R1_university():
    # URL of the Wikipedia page
    url = "https://en.wikipedia.org/wiki/List_of_research_universities_in_the_United_States"

    # Sending a request to the URL
    response = requests.get(url)

    # Parsing the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')

    # Finding the table for "Doctoral Universities – Very High Research Activity"
    table = soup.find_all("table")[0]  # soup.find_all("table", class_="wikitable sortable jquery-tablesorter")

    # Extracting the university names from the table
    universities = []
    for row in table.find_all("tr")[1:]:  # Skipping the header row
        cells = row.find_all("td")
        if len(cells) > 0:
            university_name = cells[0].get_text(strip=True)
            universities.append(university_name)
    return universities

if __name__ == "__main__":
    universities = get_R1_university()
    print(universities[:10])  # Displaying the first 10 universities for brevity
