import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qsl, quote, urlencode, urljoin, urlparse, urlunparse

base_url = "https://www.fencingdatabase.com/?firstname=&lastname=&weapon=&gender=all&tournament=all&year=all&score-fencer=all&opposing-score=all&opposing-lastname=&submit-search=Search+Clips"
foil_url = base_url.replace("weapon=", "weapon=foil")
epee_url = base_url.replace("weapon=", "weapon=epee")
sabre_url = base_url.replace("weapon=", "weapon=sabre")  


def normalize_url(url):
    parsed = urlparse(url)
    encoded_path = quote(parsed.path)
    encoded_query = urlencode(parse_qsl(parsed.query, keep_blank_values=True), doseq=True)
    return urlunparse((parsed.scheme, parsed.netloc, encoded_path, parsed.params, encoded_query, parsed.fragment))

def page_explorer(url, weapon):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    #print(soup.prettify())

    videos = soup.find_all('div', class_='video')
    print(f"Found {len(videos)} videos for {weapon}.")

    next_page_button = soup.find('a', string='Next')
    if next_page_button:
        # Resolve relative links like '?...&page=2' to a full absolute URL.
        next_page_url = normalize_url(urljoin(url, next_page_button['href']))
        print(f"Exploring next page: {next_page_url} \n")
        page_explorer(next_page_url, weapon)

page_explorer(foil_url, "foil")
# page_explorer(epee_url, "epee")
# page_explorer(sabre_url, "sabre")