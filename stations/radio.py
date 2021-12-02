# Copyright 2020 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from urllib.request import urlopen

from bs4 import BeautifulSoup

def get_radio_url():
    """Custom news scraper for Radio Text from radio.de."""
    
    domain = "http://www.wdr.de/radio"
    latest_briefings_url = f"{domain}/radiotext/"
    soup = BeautifulSoup(urlopen(latest_briefings_url), features='html.parser')
    # The collection-grid3 element contains a list of the latest episodes
    #result = soup.find_all("text_wdr3", string=True)
    #result = soup.find(id="text_wdr3").get_text()

    div = soup.find_all(id='text_wdr3')
    content = str(div)
    self.log.info(f'soup text: {content}')
    
    # Get the href value of the first link tag from within this list
    #episode_page_link = result.find_all('a')[0]['href']
    #episode_page = urlopen(domain + episode_page_link)
    #episode_soup = BeautifulSoup(episode_page, features='html.parser')
    #mp3_url = episode_soup.find_all(attrs={"data-component": "DownloadButton"})[0]['href']
    #return mp3_url
    return result
