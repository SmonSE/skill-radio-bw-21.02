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

    #url = 'https://liveradio.swr.de/sw282p3/dasding/play.mp3'  # radio stream
    url = 'https://streams.bigfm.de/bigfm-deutschland-128-mp3'  # radio stream
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

        # extract title from the metadata
        #m = re.search(br"StreamTitle='([^']*)';", metadata)
<div class="webradio-player__meta"><div class="webradio-player__track-info"><div class="webradio-track-now-label">es läuft</div><div class="webradio-track-title" data-channel-title="">Deutschlands biggste Beats</div><div class="webradio-track-meta"> <span class="webradio-track-pre-author">von</span> <span class="webradio-track-author" data-channel-artist="">Bigfm</span></div></div><div class="webradio-volume"><div class="webradio-volume__icon"> <i id="webradio-volume-icon" class="icon-volume-up" aria-hidden="true"></i></div><div class="webradio-volume__control"><div id="webradio-volume-control" class="webradio-volume__control-bar noUi-target noUi-ltr noUi-horizontal noUi-txt-dir-ltr"><div class="noUi-base"><div class="noUi-connects"><div class="noUi-connect" style="transform: translate(0%, 0px) scale(0.9, 1);"></div></div><div class="noUi-origin" style="transform: translate(-100%, 0px); z-index: 4;"><div class="noUi-handle noUi-handle-lower" data-handle="0" tabindex="0" role="slider" aria-orientation="horizontal" aria-valuemin="0.0" aria-valuemax="100.0" aria-valuenow="90.0" aria-valuetext="90.00"><div class="noUi-touch-area"></div></div></div></div></div></div><div class="webradio-volume__equalizer"><div class="webradio-equalizer"> <span class="webradio-equalizer__bar webradio-equalizer__bar--active"></span> <span class="webradio-equalizer__bar webradio-equalizer__bar--active"></span> <span class="webradio-equalizer__bar webradio-equalizer__bar--active"></span></div></div><div class="webradio-quality"> <input id="webradio-quality_toggle" class="webradio-quality_toggle" type="checkbox"> <label class="webradio-quality_toggle_button" for="webradio-quality_toggle" data-tg-on="HQ" data-tg-off="LQ"></label></div></div></div>

        m = re.search(br"player__song'([^']*)';", metadata)
        LOG.info(f'MetaData m: {m}') 

        if m:
         title = m.group(1)
         if title:
               break
        else: 
            #sys.exit('no title found')
            LOG.info("no title found.")
        
    #mp3Artist = title.decode(encoding, errors='replace')
    LOG.info(f'#META#: {title}') 

    return str(title)