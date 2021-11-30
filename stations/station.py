# Copyright 2021 Mycroft AI Inc.
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
"""Defines a Radio Station object"""

from abc import ABC, abstractproperty
from builtins import property
from pathlib import Path
from collections.abc import Callable

import feedparser
from mycroft.util import LOG

from .abc import get_abc_url
from .ft import get_ft_url
from .gpb import get_gpb_url
from .tsf import get_tsf_url


class BaseStation(ABC):
    """Abstract Base Class for all Radio Stations."""

    def __init__(self, acronym: str, full_name: str, image_file: str = None, radio_text: str = None):
        self.acronym = acronym
        self.full_name = full_name
        self.image_file = image_file
        self.radio_text = radio_text

    def as_dict(self):
        return {
            'acronym': self.acronym,
            'full_name': self.full_name,
            'image_path': str(self.image_path),
            'radio_text': str(self.radio_text),
        }

    @property
    def image_path(self) -> Path:
        """The absolute path to the stations logo.

        Note that this currently traverses the path from this file and may
        break if this is moved in the file hierarchy.
        """
        if self.image_file is None:
            return None
        skill_path = Path(__file__).parent.parent.absolute()
        file_path = Path(skill_path, 'images', self.image_file)
        if not file_path.exists():
            LOG.warning(
                f'{self.image_file} could not be found, using default image')
            file_path = Path(skill_path, 'images', 'generic.png')
        return file_path

    @abstractproperty
    def media_uri(self) -> str:
        """Get the uri for the media file to be played."""
        pass


class FileStation(BaseStation):
    """Radio Station that provides a static url for their latest briefing."""

    def __init__(self, acronym: str, full_name: str, media_url: str, image_file: str = None, radio_text: str = None):
        super().__init__(acronym, full_name, image_file, radio_text)
        self._media_url = media_url

    @property
    def media_uri(self) -> str:
        """The static media url for the station."""
        return self._media_url


class FetcherStation(BaseStation):
    """Radio Station that requires a custom url getter function."""

    def __init__(self, acronym: str, full_name: str, url_getter: Callable, image_file: str = None, radio_text: str = None):
        super().__init__(acronym, full_name, image_file, radio_text)
        self._get_media_url = url_getter

    @property
    def media_uri(self) -> str:
        """Get the uri for the media file to be played.

        Uses the stations custom getter function."""
        return self._get_media_url()


class RSSStation(BaseStation):
    """Radio Station based on an RSS feed."""

    def __init__(self, acronym: str, full_name: str, rss_url: str, image_file: str = None, radio_text: str = None):
        super().__init__(acronym, full_name, image_file, radio_text)
        self._rss_url = rss_url

    @property
    def media_uri(self) -> str:
        """Get the uri for the media file to be played."""
        media_url = self._get_audio_from_rss()
        # TODO - check on temporary workaround and remove - see issue #87
        if self._rss_url.startswith('https://www.npr.org/'):
            media_url = media_url.split('?')[0]
        return media_url

    def _get_audio_from_rss(self) -> str:
        """Get the first audio url from the Station RSS feed.

        Selects the first link to an audio file, or falls back to the
        first href link in the entry if no explicit audio can be found.

        Args:
            rss_url: RSS feed to parse

        Returns:
            Url to a media file or None if no link can be found.
        """
        audio_url = None
        data = feedparser.parse(self._rss_url)
        if data.entries:
            # select the first link to an audio file
            for link in data['entries'][0]['links']:
                if 'audio' in link['type']:
                    audio_url = link['href']
                    break
                else:
                    # fall back to using the first link in the entry
                    audio_url = data['entries'][0]['links'][0]['href']
        return audio_url


def create_custom_station(station_url):
    """Create a new station from a custom url.

    First tests to see if the url can be read as an RSS feed, if not assumes it is a
    direct link.

    NOTE: it cannot be a FetcherStation because you can't define the fetching function.
    """
    is_rss_feed = feedparser.parse(station_url).entries > 0
    if is_rss_feed:
        clazz = RSSStation
    else:
        clazz = FileStation
    stations['custom'] = clazz('custom', 'Your custom station', station_url)


# NOTE: This list should be kept in sync with the settingsmeta select options,
# however modifying that file will cause the backend to consider it as a new
# group of settings. Until there is a better mechanism for handling updated
# settingsmeta files, we will not be adding new stations to the settings.
# They can be added to the list of country defaults below.

stations = dict(

    ##RadioStation ## https://radiome.de/baden-wurttemberg  // http://fmstream.org/index.php?i=1352
    ##Baden-Württemberg (BW)
    BFM=FileStation('bigFM', 'bigFM', 
                    'http://streams.bigfm.de/bigfm-bw-128-mp3', 'BFM.png', 'None'),
    DD=FileStation('DASDING', 'DASDING', 
                    'https://liveradio.swr.de/sw282p3/dasding/play.mp3', 'DD.png', 'Radiotext muss ich noch hier rein bekommen'),
    RGB=FileStation('REGNBGN', 'REGENBOGEN',
                    'https://streams.regenbogen.de/rr-mannheim-128-mp3', 'RGB.png', 'None'),
    SWR3=FileStation('SWR3', 'SWR3 Radio',
                    'https://liveradio.swr.de/sw282p3/swr3/play.mp3', 'SWR3.png', 'None'),
    SWR1R=FileStation('SWR1', 'SWR1 BW Radio',
                    'https://liveradio.swr.de/sw282p3/swr1bw/play.mp3', 'SWR1R.png', 'None'),
    DNW=FileStation('DNW', 'Die neue Welle',
                    'http://dieneuewelle.cast.addradio.de/dieneuewelle/simulcast/high/stream.mp3', 'DNW.png', 'None'),
    SHL=FileStation('sunshine', 'sunshile live',
                    'http://stream.sunshine-live.de/hq/mp3-128', 'SHL.png', 'None'),
    SWR4S=FileStation('SWR4 S', 'SWR4 Stuttgart',
                    'http://swr-swr4-bw.cast.addradio.de/swr/swr4/bw/mp3/128/stream.mp3', 'SWR4F.png', 'None'),
    SWR4K=FileStation('SWR4 KA', 'SWR4 Karlsruhe',
                    'http://swr-swr4-ka.cast.addradio.de/swr/swr4/ka/mp3/128/stream.mp3', 'SWR4F.png', 'None'),
    ANT=FileStation('antenne1', 'antenne 1',
                    'http://stream.antenne1.de/a1stg/livestream2.mp3', 'ANT.png', 'None'),
    RD7=FileStation('radio7', 'Radio 7',
                    'http://radio7server.streamr.ru:8040/radio7256.mp3', 'RD7.png', 'None'),
    SWR2=FileStation('swr2', 'SWR 2',
                    'https://liveradio.swr.de/sw331ch/swr2', 'SWR2.png', 'None'),
    ENY=FileStation('energy', 'Energy Stuttgart',
                    'http://media.mediatime.ru:8051/Energy', 'ENY.png', 'None'),
    BAD=FileStation('baden.fm', 'Baden FM',
                    'http://badenfm.ip-streaming.net:8006/badenfm', 'BAD.png', 'None'),
    EPR=FileStation('europa-park', 'Europa-Park Radio',
                    'https://rs9.stream24.net/europa-park-radio.mp3', 'EPR.png', 'None'),                   
    SEE=FileStation('seefunk', 'Radio Seefunk',
                    'http://webradio.radio-seefunk.de:8000/live64', 'SEE.png', 'None'),  
    BHH=FileStation('bigFM Hip Hop', 'big FM Hip Hop',
                    'http://streams.bigfm.de/bigfm-dhiphopcharts-128-mp3', 'BFM.png', 'None'),  
    BHC=FileStation('bigFM Charts', 'big FM Charts',
                    'http://ilr.bigfm.de/bigfm-charts-128-mp3', 'BFM.png', 'None'), 
    RLR=FileStation('Rockland', 'Rockland Radio',
                    'http://stream.rockland.de/rockland.mp3', 'RLR.png', 'None'), 
    SWRA=FileStation('SWR Aktuell', 'SWR Aktuell',
                    'http://liveradio.swr.de/sw282p3/swraktuell/play.mp3', 'SWRA.png', 'None'), 
    
    #WDR3=FileStation('WDR3', 'WDR3', 'http://wdr-wdr3-live.icecast.wdr.de/wdr/wdr3/live/mp3/128/stream.mp3', 'SWRA.png', 'http://www.wdr.de/radio/radiotext/streamtitle_wdr3.txt'), 


                
)
# Country Default -> should be change to Region default
country_defaults = dict(
    AT='OE3',
    AU='ABC',
    BE='VRT',
    CA='CBC',
    DE='SWR3',
    ES='RNE',
    FI='YLE',
    PT='TSF',
    SE='Ekot',
    UK='BBC',
    US='NPR',
)
