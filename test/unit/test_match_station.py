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
#
import unittest

from stations import stations
from stations.match import (
    CONF_EXACT_MATCH,
    CONF_LIKELY_MATCH,
    CONF_GENERIC_MATCH,
    match_station_from_utterance, 
    match_station_name
)


class TestSingleStationMatching(unittest.TestCase):

    def match_npr_name(self, phrase):
        return match_station_name(phrase, stations['SWR3'], 'radio')
    
    def test_strong_match_of_station_name(self):
        test_phrases_with_strong_match = [
            'SWR3',
            'SWR3 radio',
        ]
        for phrase in test_phrases_with_strong_match:
            station_match, confidence = self.match_npr_name(phrase)
            self.assertEqual(station_match, stations['SWR3'])
            self.assertTrue(confidence >= CONF_EXACT_MATCH)

    def test_likely_match_of_station_name(self):
        test_phrases_with_likely_match = [
            'the SWR3 radio',
        ]
        for phrase in test_phrases_with_likely_match:
            station_match, confidence = self.match_npr_name(phrase)
            self.assertEqual(station_match, stations['SWR3'])
            self.assertTrue(CONF_EXACT_MATCH > confidence >= CONF_LIKELY_MATCH)

    def test_generic_match_of_station_name(self):
        test_phrases_with_generic_match = [
            'what is on SWR3 radio',
            'play the SWR3',
            'radio',
        ]
        for phrase in test_phrases_with_generic_match:
            station_match, confidence = self.match_npr_name(phrase)
            self.assertEqual(station_match, stations['SWR3'])
            self.assertTrue(CONF_LIKELY_MATCH > confidence >= CONF_GENERIC_MATCH)

    def test_weak_match_of_station_name(self):
        test_phrases_with_weak_match = [
            'I wonder what might be on SWR3 right now',
            'test',
            'banana',
        ]
        for phrase in test_phrases_with_weak_match:
            station_match, confidence = self.match_npr_name(phrase)
            self.assertEqual(station_match, stations['SWR3'])
            self.assertTrue(0 < confidence < CONF_GENERIC_MATCH)


class TestMatchStationFromUtterance(unittest.TestCase):

    def test_generic_radio_request(self):
        test_utterances = [
            ''
        ]