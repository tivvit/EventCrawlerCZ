__author__ = 'tivvit'

import EncodingHelper

from google.appengine.api import urlfetch
from BeautifulSoup import BeautifulSoup
from datetime import datetime

class srazyinfoParser():
    structuredEvents = []
    url = "http://srazy.info/"

    def __init__(self):
        rpc = urlfetch.create_rpc(deadline=60)
        urlfetch.make_fetch_call(rpc, self.url)

        rpcs = []

        try:
            result = rpc.get_result()
            if result.status_code == 200:
                content = EncodingHelper.getEncodedContent(result)
                soup = BeautifulSoup(content)

                events = soup.find(id='nextPages').findChildren('div', attrs={"class": "media"})

                for event in events:
                    mediaBody = event.findChild('div', attrs={"class": "media-body"})
                    structuredEvent = {}
                    structuredEvent['source'] = self.url
                    structuredEvent['url'] = self.url+mediaBody.findChild('h4').findChild('a').get('href')
                    structuredEvent['title'] = mediaBody.findChild('h4').findChild('a').string
                    structuredEvent['img'] = self.url+event.findChild('img').get('src')
                    datestr = str(mediaBody.findChild('span', attrs={"class": "stream-event-meta"}).string).strip().translate(None, ' ')
                    if datestr != 'None':
                        structuredEvent['date'] = datetime.strptime(datestr, "%d.%m.%Y").date()
                    else:
                        structuredEvent['date'] = None
                    structuredEvent['text'] = mediaBody.findChild('p').string.strip()
                    structuredEvent['place'] = ''
                    self.structuredEvents.append(structuredEvent)

                    '''
                    innerRpc = urlfetch.create_rpc(deadline=60)
                    innerRpc.callback = self.create_callback(innerRpc)
                    urlfetch.make_fetch_call(innerRpc, structuredEvent['url'], follow_redirects=False)
                    rpcs.append(innerRpc)
                    '''

        except urlfetch.DownloadError:
            self.response.write("chyba stahovani")

        for irpc in rpcs:
            irpc.wait()

    def create_callback(self, rpc):
        return lambda: self.handleDetails(rpc)

    def handleDetails(self, rpc):
        try:
            result = rpc.get_result()
            url = str(rpc.request).splitlines()[1].split(' ')[1][1:-1]
            for event in self.structuredEvents:
                if event['url'] == url:
                    soup = BeautifulSoup(EncodingHelper.getEncodedContent(result))
                    baseElement = soup.find('div',  attrs={"class": "node-inner odd"})
                    event['text'] = baseElement.findChild('div', attrs={"class": "detail clearfix"})
                    date = str(baseElement.findChild('div', attrs={"class": "submitted"}).contents[3]).strip()
                    event['date'] = datetime.strptime(date, "%d.%m.%Y").date()
            return 0
        except urlfetch.DownloadError:
                self.response.write("chyba stahovani")