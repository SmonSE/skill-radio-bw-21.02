# https://stackoverflow.com/questions/35102278/python-3-get-song-name-from-internet-radio-stream

from __future__ import print_function
from mycroft.util import LOG
import re
import struct
import sys
try:
    import urllib2
except ImportError:  # Python 3
    import urllib.request as urllib2

def get_streamContent_url():

    url = 'https://liveradio.swr.de/sw282p3/dasding/play.mp3'  # radio stream
    encoding = 'latin1' # default: iso-8859-1 for mp3 and utf-8 for ogg streams
    request = urllib2.Request(url, headers={'Icy-MetaData': 1})  # request metadata
    response = urllib2.urlopen(request)
    #LOG.info(response.headers)

    metaint = int(response.headers['icy-metaint'])
    for _ in range(10): # # title may be empty initially, try several times
        response.read(metaint)  # skip to metadata
        metadata_length = struct.unpack('B', response.read(1))[0] * 16  # length byte
        metadata = response.read(metadata_length).rstrip(b'\0')
        LOG.info(f'MetaData length: {metadata_length}')
        #LOG.info(f'MetaData: {metadata}')

        # extract title from the metadata
        m = re.search(br"StreamTitle='([^']*)';", metadata)
        if m:
         title = m.group(1)
         if title:
               break
        else: 
            sys.exit('no title found')
            LOG.info("This is an info level log message.")
        
    #LOG.info(f'Title: {title.decode()}')
    mp3Artist = title.decode(encoding, errors='replace')
    LOG.info("### DREI ###")

    return mp3Artist