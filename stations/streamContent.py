# https://stackoverflow.com/questions/35102278/python-3-get-song-name-from-internet-radio-stream

from __future__ import print_function
from urllib.request import urlopen
import re
import struct
import sys
try:
    import urllib2
except ImportError:  # Python 3
    import urllib.request as urllib2

def get_streamContent_url():

    url = 'https://liveradio.swr.de/sw282p3/dasding/play.mp3'  # radio stream
    encoding = 'default' # default: iso-8859-1 for mp3 and utf-8 for ogg streams
    request = urllib2.Request(url, headers={'Icy-MetaData': 1})  # request metadata
    response = urllib2.urlopen(request)
    self.log.info(f'get_streamContent_url::respponse.headers: {response.headers}')
    print(response.headers, file=sys.stderr)

    metaint = int(response.headers['icy-metaint'])
    for _ in range(10): # # title may be empty initially, try several times
        response.read(metaint)  # skip to metadata
        metadata_length = struct.unpack('B', response.read(1))[0] * 16  # length byte
        metadata = response.read(metadata_length).rstrip(b'\0')
        print(metadata, file=sys.stderr)
        self.log.info(f'get_streamContent_url::metadata: {metadata}')

        # extract title from the metadata
        m = re.search(br"StreamTitle='([^']*)';", metadata)
        if m:
         title = m.group(1)
         if title:
               break
        else: 
            sys.exit('no title found')
        
        print(title.decode(encoding, errors='replace'))
        self.log.info(f'get_streamContent_url::title.decode: {title.decode(encoding, errors='replace')}')
        mp3Artist = title.decode(encoding, errors='replace')

        return mp3Artist