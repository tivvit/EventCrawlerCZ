__author__ = 'tivvit'

import EncodingHelper

from google.appengine.api import urlfetch
from BeautifulSoup import BeautifulSoup
from datetime import datetime


class bizitParser():
    structuredEvents = []
    url = "http://bizit.cz/"

    def __init__(self):
        rpc = urlfetch.create_rpc(deadline=60)
        urlfetch.make_fetch_call(rpc, self.url)

        rpcs = []

        try:
            result = rpc.get_result()
            if result.status_code == 200:
                content = EncodingHelper.getEncodedContent(result)
                soup = BeautifulSoup(content)

                events = soup.find(id='hp-articles').findChildren('a')

                for event in events:
                    structuredEvent = {}
                    structuredEvent['source'] = self.url
                    structuredEvent['url'] = self.url+event.get('href')
                    structuredEvent['title'] = event.findChild('h2').string
                    structuredEvent['img'] = event.findChild('img').get('src')
                    structuredEvent['place'] = event.findChild('div', attrs={"class": "hp-article-title"}).string
                    self.structuredEvents.append(structuredEvent)

                    innerRpc = urlfetch.create_rpc(deadline=60)
                    innerRpc.callback = self.create_callback(innerRpc)
                    urlfetch.make_fetch_call(innerRpc, structuredEvent['url'], follow_redirects=False)
                    rpcs.append(innerRpc)

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
                    text = ""
                    for p in baseElement.findChild('div', attrs={"class": "detail clearfix"}).findChildren('p'):
                        text += "<p>"+p.text+"</p>"
                    event['text'] = text
                    event['date'] = datetime.strptime(baseElement.findChild('div', attrs={"class": "submitted"}).contents[3].strip(), "%d.%m.%Y")
            return 0
        except urlfetch.DownloadError:
                self.response.write("chyba stahovani")