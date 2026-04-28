import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qsl, quote, urlencode, urljoin, urlparse, urlunparse
import os

base_url = "https://www.fencingdatabase.com/"
url_params = "?firstname=&lastname=&weapon=&gender=all&tournament=all&year=all&score-fencer=all&opposing-score=all&opposing-lastname=&submit-search=Search+Clips"
foil_url = base_url + url_params.replace("weapon=", "weapon=foil")
epee_url = base_url + url_params.replace("weapon=", "weapon=epee")
sabre_url = base_url + url_params.replace("weapon=", "weapon=sabre")  


def normalize_url(url):
    parsed = urlparse(url)
    encoded_path = quote(parsed.path)
    encoded_query = urlencode(parse_qsl(parsed.query, keep_blank_values=True), doseq=True)
    return urlunparse((parsed.scheme, parsed.netloc, encoded_path, parsed.params, encoded_query, parsed.fragment))

def save_video(video_url, weapon, touch):
    response = requests.get(video_url, stream=True)
    if response.status_code == 200:
        if not os.path.exists(weapon):
            os.makedirs(weapon)
        if not os.path.exists(os.path.join(weapon, touch)):
            os.makedirs(os.path.join(weapon, touch))
        video_name = video_url.split('/')[-1]
        video_path = os.path.join(weapon, touch, video_name)
        with open(video_path, 'wb') as video_file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    video_file.write(chunk)
        print(f"Saved video to: {video_path}")
    else:
        print(f"Failed to download video: {video_url}, status code: {response.status_code}")

def page_explorer(base_url, url, weapon):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    #print(soup.prettify())
    videos = soup.find_all('div', class_='video')
    for video in videos:
        video_url = video.find('a')['href']
        video_page = requests.get(base_url + video_url)
        video_soup = BeautifulSoup(video_page.text, 'html.parser')
        #print(video_soup.prettify())
        video_touch = video_soup.find('div', class_='gfycat-info').find('div').text.replace("Touch: ", "").lower()
        full_video_url = video_soup.find('video').find('source')['src']
        save_video(full_video_url, weapon, video_touch)

    next_page_button = soup.find('a', string='Next')
    if next_page_button:
        # Resolve relative links like '?...&page=2' to a full absolute URL.
        next_page_url = normalize_url(urljoin(url, next_page_button['href']))
        print(f"Exploring next page: {next_page_url} \n")
        print("--------------------------------------------------\n")
        page_explorer(base_url, next_page_url, weapon)

page_explorer(base_url, foil_url, "foil")
# page_explorer(base_url, epee_url, "epee")
# page_explorer(base_url, sabre_url, "sabre")