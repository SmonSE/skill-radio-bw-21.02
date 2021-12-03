# 
#
#

from __future__ import print_function
from mycroft.util import LOG
import re
import struct
import sys
try:
    import urllib2
except ImportError:  # Python 3
    import urllib.request as urllib2

def __init__(self, title: str = None):
        self.title = title

def as_dict(self):
        return {
            'title': self.title,
        }

def get_streamContent_url(self) -> str:

    url = 'https://liveradio.swr.de/sw282p3/dasding/play.mp3'  # radio stream
    #url = 'https://streams.bigfm.de/bigfm-deutschland-128-mp3'  # radio stream
    encoding = 'latin1' # default: iso-8859-1 for mp3 and utf-8 for ogg streams
    request = urllib2.Request(url, headers={'Icy-MetaData': 1})  # request metadata
    response = urllib2.urlopen(request)
    #LOG.info(response.headers)

    metaint = int(response.headers['icy-metaint'])
    for _ in range(10): # # title may be empty initially, try several times
        response.read(metaint)  # skip to metadata
        metadata_length = struct.unpack('B', response.read(1))[0] * 16  # length byte
        metadata = response.read(metadata_length).rstrip(b'\0')
        #LOG.info(f'MetaData length: {metadata_length}')

        # extract title from the metadata
        #MetaData m: <_sre.SRE_Match object; span=(11, 51), match=b"='Bitch better have my money - Rihanna';">
        meta = re.search(br"'([^']*)';", metadata)
        LOG.info(f'MetaData: {meta}') 

        if meta:
         title = meta.group(1)
         if title:
               break
        else: 
            sys.exit('no meta data found')
            LOG.info("no meta data found.")
        
    #mp3Artist = title.decode(encoding, errors='replace')
    LOG.info(f'#META#: {title}') 
    return title