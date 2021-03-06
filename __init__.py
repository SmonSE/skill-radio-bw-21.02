# Copyright 2018 Mycroft AI Inc.
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

import os
import subprocess
import time
from datetime import datetime

from urllib.parse import quote
from mycroft import intent_handler, AdaptIntent
from mycroft.audio import wait_while_speaking # -> issue PiCroft wait while speaking (no audio)!!!
from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel
from mycroft.util import get_cache_directory

from .stations.match import match_station_from_utterance, Match
from .stations.station import create_custom_station, BaseStation, country_defaults, stations
from .stations.util import contains_html, find_mime_type

from .stations.streamContent import find_metaData_url

# Minimum confidence levels
CONF_EXACT_MATCH = 0.9
CONF_LIKELY_MATCH = 0.7
CONF_GENERIC_MATCH = 0.6


class RadioSkill(CommonPlaySkill):
    def __init__(self):
        super().__init__(name="RadioSkill")
        self.now_playing = None
        self.last_station_played = None
        self.curl = None

    def initialize(self):
        time.sleep(1)
        self.log.debug('Disabling restart intent')
        self.disable_intent('restart_playback')
        # Longer titles or alternative common names of feeds for searching
        self.alternate_station_names = self.load_alternate_station_names()
        self.settings_change_callback = self.on_websettings_changed
        # Check Settings from Mycroft AI WEB
        self.on_websettings_changed()

    def load_alternate_station_names(self) -> dict:
        """Load the list of alternate station names from alt.feed.name.value
        These are provided as name, acronym pairs. They are reordered into a
        dict keyed by acronym for ease of use in station matching.
        Returns:
            Dict of alternative names for stations
                Keys: station acronym
                Values: list of alternative names
        """
        loaded_list = self.translate_namedvalues('alt.feed.name')
        alternate_station_names = {}
        for name in loaded_list:
            acronym = loaded_list[name]
            if alternate_station_names.get(acronym) is None:
                alternate_station_names[acronym] = []
            alternate_station_names[acronym].append(name)
        return alternate_station_names

    # mycroft.ai skills websettings
    def on_websettings_changed(self):
        """Callback triggered anytime Skill settings are modified on backend."""
        station_code = self.settings.get("station", "not_set")
        custom_url = self.settings.get("custom_url", "")
        if station_code == "not_set" and len(custom_url) > 0:
            self.log.info("Creating custom Radio Station from Skill settings.")
            create_custom_station(custom_url)

    @intent_handler(AdaptIntent("").one_of("Give", "Latest").require("Radio"))
    def handle_latest_radio(self, message):
        """Adapt intent handler to capture general queries for the latest Radio."""
        match = match_station_from_utterance(self, message.data['utterance'])
        if match and match.station:
            station = match.station
        else:
            station = self.get_default_station()
        self.handle_play_request(station)

    @intent_handler("PlayTheRadio.intent")
    def handle_latest_radio_alt(self, message):
        """Padatious intent handler to capture short distinct utterances."""
        match = match_station_from_utterance(self, message.data['utterance'])
        if match and match.station:
            station = match.station
        else:
            station = self.get_default_station()
        self.handle_play_request(station)

    @intent_handler(AdaptIntent('').require('Restart'))
    def restart_playback(self, message):
        self.log.info('Restarting last station to be played')
        if self.last_station_played:
            self.handle_play_request(self.last_station_played)

    def CPS_start(self, _, data):
        """Handle request from Common Play System to start playback."""
        if data and data.get('acronym'):
            # Play the requested Radio service
            selected_station = stations[data['acronym']]
        else:
            # Just use the default Radio feed
            selected_station = self.get_default_station()
        self.handle_play_request(selected_station)

    def CPS_match_query_phrase(self, phrase: str) -> tuple((str, float, dict)):
        """Respond to Common Play Service query requests.
        Args:
            phrase: utterance request to parse
        Returns:
            Tuple(Name of station, confidence, Station information)
        """
        if not self.voc_match(phrase.lower(), 'Radio'):
            # The utterance does not contain radio vocab. Do not match.
            return None
        match = match_station_from_utterance(self, phrase)

        # If no match but utterance contains radio, return low confidence level
        if match.confidence < CONF_GENERIC_MATCH:
            match = Match(self.get_default_station(), CONF_GENERIC_MATCH)

        # Translate match confidence levels to CPSMatchLevels
        if match.confidence >= CONF_EXACT_MATCH:
            match_level = CPSMatchLevel.EXACT
        elif match.confidence >= CONF_LIKELY_MATCH:
            match_level = CPSMatchLevel.ARTIST
        elif match.confidence >= CONF_GENERIC_MATCH:
            match_level = CPSMatchLevel.CATEGORY
        else:
            return None

        return (match.station.full_name, match_level, match.station.as_dict())

    def download_media_file(self, url: str) -> str:
        """Download a media file and return path to the stream.
        Args:
            url (str): media file to download
        Returns:
            stream (str): file path of the audio stream
        Raises:
            ValueError if url does not provide a valid audio file
        """
        stream = '{}/stream'.format(get_cache_directory('RadioSkill'))
        # (Re)create Fifo
        if os.path.exists(stream):
            os.remove(stream)
        os.mkfifo(stream)
        self.log.debug('Running curl {}'.format(url))
        args = ['curl', '-L', quote(url, safe=":/"), '-o', stream]
        self.curl = subprocess.Popen(args)
        # Check if downloaded file is actually an error page
        if contains_html(stream):
            raise ValueError('Could not fetch valid audio file.')
        return stream

    def get_default_station(self) -> BaseStation:
        """Get default station for user.
        Fallback order:
        1. Station defined in Skill Settings
        2. Default station for country
        3. SWR3 Radio as global default
        """
        station = None
        station_code = self.settings.get('station', 'not_set')
        custom_url = self.settings.get('custom_url', '')
        if station_code != 'not_set':
            station = stations[station_code]
        elif len(custom_url) > 0:
            station = stations.get('custom')
        if station is None:
            station = self.get_default_station_by_country()
        if station is None:
            station = stations['SWR3']
        return station

    def get_default_station_by_country(self) -> BaseStation:
        """Get the default station based on the devices location."""
        country_code = self.location['city']['state']['country']['code']
        station_code = country_defaults.get(country_code)
        return stations.get(station_code)


    def handle_play_request(self, station: BaseStation = None):
        """Handle request to play a station.
        Args:
            station: Instance of a Station to be played
        """
        self.stop()
        # Speak intro while downloading in background
        self.speak_dialog('radio', data={"from": station.full_name})
        self._play_station(station)
        self.last_station_played = station
        self.enable_intent('restart_playback')

    @property
    def is_https_supported(self) -> bool:
        """Check if any available audioservice backend supports https."""
        for service in self.audioservice.available_backends().values():
            if 'https' in service['supported_uris']:
                return True
        return False

    def show_image(self, url, caption=None,
                   title=None, fill=None,
                   override_idle=None, override_animations=False):
        """Display a GUI page for viewing an image.
            Args:
                url (str): Pointer to the image
                caption (str): A caption to show under the image
                title (str): A title to display above the image content
                fill (str): Fill type supports 'PreserveAspectFit',
                'PreserveAspectCrop', 'Stretch'
                override_idle (boolean, int):
                    True: Takes over the resting page indefinitely
                    (int): Delays resting page for the specified number of seconds.
            override_animations (boolean):
                True: Disables showing all platform skill animations.
                False: 'Default' always show animations.
        """
        self["image"] = url
        self["title"] = title
        self["caption"] = caption
        self["fill"] = fill
        self.show_page("SYSTEM_ImageFrame.qml", override_idle,
                       override_animations)


    def current_time_radio(self) -> str:
        """Format a the datetime into a string for GUI display."""    
        now = datetime.now() # current date and time
        timeToShow = now.strftime("%H:%M:%S")    
        #self.log.info(f'Radio Time: {timeToShow}')       
        return timeToShow 


    def update_station_content(self, station: BaseStation = None) -> str:
        """Update the station content to gui permantent."""
        self.log.info("Update GUI every 10 seconds update_station_content")
        med_url = station.media_uri
        self.log.info(f'Radio media url from update_station_content: {med_url}')
        artistTitle = find_metaData_url(med_url)
        self.log.info(f'ArtistTitle from update_station_content: {med_url}')
        return artistTitle


    def _play_station(self, station: BaseStation):
        """Play the given station using the most appropriate service.    
        Args: 
            station (Station): Instance of a Station to be played
        """
        try:
            self.log.info(f'Playing Radio feed _play_station: {station.full_name}')
            media_url = station.media_uri
            self.log.info(f'Radio media url _play_station: {media_url}')
            mime = find_mime_type(media_url)

            self.log.info(f'Station acronym _play_station: {station.acronym}')
            #self.log.info(f'Station image file _play_station: {station.image_file}')
            self.log.info(f'Station logo url _play_station: {station.station_logo_url}')
            self.log.info(f'Radio Time _play_station: {self.current_time_radio()}')      

            artist_Title = find_metaData_url(media_url)
            self.log.info(f'Artist from _play_station: {artist_Title}')

            # Ensure announcement of station has finished before playing
            
            #wait_while_speaking() -> current issue in Picroft (no audio) !!!
            time.sleep(1)
            # If backend cannot handle https, download the file and provide a local stream.

            #if media_url[:8] == 'https://' and not self.is_https_supported:
            stream = self.download_media_file(media_url)
            self.CPS_play((f"file://{stream}", mime))
            self.log.info("### download stream for playing ###")
            #else:
            #    self.CPS_play((media_url, mime))
            #    self.log.info("#### ELSE ####")
            self.CPS_send_status(
                # cast to str for json serialization
                #image=str(station.image_path),
                artist=station.full_name
            )
            self.now_playing = station.full_name
        except ValueError as e:
            self.speak_dialog("could.not.start.the.radio.feed")
            self.log.exception(e)

    def stop_curl_process(self):
        """Stop any running curl download process."""
        if self.curl:
            try:
                self.curl.terminate()
                self.curl.communicate()
                # Check if process has completed
                return_code = self.curl.poll()
                if return_code is None:
                    # Process must still be running...
                    self.curl.kill()
                else:
                    self.log.debug(f'Curl return code: {return_code}')
            except subprocess.SubprocessError as e:
                self.log.exception(f'Could not stop curl: {repr(e)}')
            finally:
                self.curl = None
    def stop(self) -> bool:
        """Respond to system stop commands."""
        if self.now_playing is None:
            return False
        self.now_playing = None
        # Disable restarting when stopped
        if self.last_station_played:
            self.disable_intent('restart_playback')
            self.last_station_played = None
        # Stop download process if it's running.
        self.stop_curl_process()
        self.CPS_send_status()
        return True

def create_skill():
    return RadioSkill()

