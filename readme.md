- GAE application
- BeautifulSoap for parsing

normalizes event data from these pages
- [bizit.cz](http://bizit.cz)
- [srazy.info](http://srazy.info)

stores them in datastore (if not duplicate)

crawls source pages every 4 hours

- check title page for new events
- crawls event detail page

print upcoming ordered events (from all sources)